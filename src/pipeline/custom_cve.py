"""
src/pipeline/custom_cve.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Enables manual and on-demand ingestion of CVEs not present in the pre-collected dataset.
Supports querying NIST NVD REST API v2 on demand, CISA KEV matching, contextual risk
scoring calculation, and persistent storage in SQLite and Streamlit session state.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.scoring.contextual import ContextualRiskScorer

logger = logging.getLogger(__name__)

_CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)
_NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def is_valid_cve_id(cve_id: str) -> bool:
    """Validate CVE identifier format (e.g. 'CVE-2024-3400')."""
    return bool(_CVE_REGEX.match(cve_id.strip()))


def fetch_nvd_cve_details(cve_id: str, api_key: str | None = None, timeout: int = 15) -> dict[str, Any] | None:
    """Fetch vulnerability metadata on-demand from NIST NVD REST API v2.

    Parameters
    ----------
    cve_id:
        CVE identifier (e.g. ``"CVE-2024-3400"``).
    api_key:
        Optional NVD API key to bypass unauthenticated rate-limits.
    timeout:
        HTTP request timeout in seconds.

    Returns
    -------
    dict | None:
        Extracted metadata dictionary with keys ``cve_id``, ``description``,
        ``cvss_v3_score``, ``cvss_v3_severity``, ``cvss_v3_vector``,
        ``affected_products``, ``published_date``. Returns None on failure.
    """
    cleaned_id = cve_id.strip().upper()
    headers = {"Accept": "application/json"}
    if api_key:
        headers["apiKey"] = api_key

    params = {"cveId": cleaned_id}

    try:
        response = requests.get(_NVD_BASE_URL, headers=headers, params=params, timeout=timeout)
        if response.status_code != 200:
            logger.warning("NVD API returned status %d for %s", response.status_code, cleaned_id)
            return None

        payload = response.json()
        vulns = payload.get("vulnerabilities", [])
        if not vulns:
            return None

        cve_obj = vulns[0].get("cve", {})

        # 1. Description
        descriptions = cve_obj.get("descriptions", [])
        desc = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")
        if not desc and descriptions:
            desc = descriptions[0].get("value", "")

        # 2. CVSS score & severity (CVSS 3.1 -> CVSS 3.0 -> CVSS 2.0)
        metrics = cve_obj.get("metrics", {})
        cvss_score: float | None = None
        cvss_severity: str = "MEDIUM"
        cvss_vector: str = ""

        for key in ("cvssMetricV31", "cvssMetricV30"):
            metric_list = metrics.get(key, [])
            if metric_list:
                primary = next((m for m in metric_list if m.get("type") == "Primary"), metric_list[0])
                cvss_data = primary.get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                cvss_severity = cvss_data.get("baseSeverity", "MEDIUM").upper()
                cvss_vector = cvss_data.get("vectorString", "")
                break

        if cvss_score is None and "cvssMetricV2" in metrics:
            metric_list = metrics.get("cvssMetricV2", [])
            if metric_list:
                primary = metric_list[0]
                cvss_data = primary.get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                cvss_severity = primary.get("baseSeverity", "MEDIUM").upper()
                cvss_vector = cvss_data.get("vectorString", "")

        # 3. Affected Products (CPE criteria strings)
        products: list[str] = []
        for config in cve_obj.get("configurations", []):
            for node in config.get("nodes", []):
                for match in node.get("cpeMatch", []):
                    crit = match.get("criteria", "")
                    if crit:
                        parts = crit.split(":")
                        if len(parts) >= 5:
                            vendor, prod = parts[3], parts[4]
                            entry = f"{vendor} {prod}".replace("_", " ").strip()
                            if entry and entry not in products:
                                products.append(entry)

        affected_str = ", ".join(products[:8]) if products else ""

        return {
            "cve_id": cleaned_id,
            "description": desc,
            "cvss_v3_score": float(cvss_score) if cvss_score is not None else 5.0,
            "cvss_v3_severity": cvss_severity or "MEDIUM",
            "cvss_v3_vector": cvss_vector,
            "affected_products": affected_str,
            "published_date": cve_obj.get("published", ""),
            "last_modified": cve_obj.get("lastModified", ""),
        }

    except Exception as exc:
        logger.warning("Failed fetching %s from NVD API: %s", cleaned_id, exc)
        return None


def check_cisa_kev_status(cve_id: str, raw_kev_path: Path | str | None = None) -> bool:
    """Check if a CVE is listed in CISA Known Exploited Vulnerabilities catalog."""
    cleaned_id = cve_id.strip().upper()
    if raw_kev_path is None:
        raw_kev_path = Path(__file__).resolve().parents[2] / "data" / "raw" / "kev_raw.json"

    p = Path(raw_kev_path)
    if p.exists():
        try:
            with p.open(encoding="utf-8") as fh:
                data = json.load(fh)
                vulns = data.get("vulnerabilities", [])
                for v in vulns:
                    if v.get("cveID", "").upper() == cleaned_id:
                        return True
        except Exception as exc:
            logger.error("Error reading KEV file: %s", exc)

    return False


def calculate_custom_risk(
    cvss_score: float,
    in_kev: bool,
    asset: dict[str, Any] | None = None,
) -> tuple[float, str]:
    """Calculate contextual risk score and band using standard formula."""
    scorer = ContextualRiskScorer()
    dummy_series = pd.Series({"cvss_v3_score": cvss_score, "in_kev": in_kev})
    risk = scorer.score_vulnerability(dummy_series, asset)
    band = scorer.get_risk_band(risk)
    return round(risk, 4), band


def ingest_custom_cve(
    vuln_df: pd.DataFrame,
    cve_data: dict[str, Any],
    db_path: Path | str | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Add or update a custom CVE in the DataFrame and optionally SQLite database.

    Recalculates ``rank_cvss``, ``rank_contextual``, and ``rank_displacement``
    across the entire dataset.

    Parameters
    ----------
    vuln_df:
        The current vulnerability DataFrame.
    cve_data:
        Dict containing at minimum ``cve_id``, ``cvss_v3_score``, ``in_kev``,
        ``description``, ``affected_products``, and optionally ``matched_asset_id``,
        ``risk_score``, ``risk_band``.
    db_path:
        Optional path to SQLite database for persistence.

    Returns
    -------
    tuple[pd.DataFrame, pd.Series]:
        Updated DataFrame and the newly inserted/updated Series.
    """
    df = vuln_df.copy() if vuln_df is not None and not vuln_df.empty else pd.DataFrame()

    cve_id = str(cve_data["cve_id"]).strip().upper()
    cvss_score = float(cve_data.get("cvss_v3_score", 5.0) or 5.0)
    in_kev = bool(cve_data.get("in_kev", False))
    severity = str(cve_data.get("cvss_v3_severity", "MEDIUM")).upper()
    desc = str(cve_data.get("description", ""))
    products = str(cve_data.get("affected_products", ""))
    matched_asset_id = str(cve_data.get("matched_asset_id", ""))
    risk_score = float(cve_data.get("risk_score", 0.0) or 0.0)
    risk_band = str(cve_data.get("risk_band", "Medium"))

    record = {
        "cve_id": cve_id,
        "cvss_v3_score": cvss_score,
        "cvss_score": cvss_score,
        "cvss_v3_severity": severity,
        "cvss_severity": severity,
        "cvss_v3_vector": cve_data.get("cvss_v3_vector", ""),
        "cvss_vector": cve_data.get("cvss_v3_vector", ""),
        "in_kev": in_kev,
        "published_date": cve_data.get("published_date", ""),
        "last_modified": cve_data.get("last_modified", ""),
        "description": desc,
        "affected_products": products,
        "references_": cve_data.get("references_", ""),
        "vendor_project": cve_data.get("vendor_project", ""),
        "product": cve_data.get("product", ""),
        "vulnerability_name": cve_data.get("vulnerability_name", cve_id),
        "date_added_kev": cve_data.get("date_added_kev", ""),
        "risk_score": risk_score,
        "risk_band": risk_band,
        "matched_asset_id": matched_asset_id,
    }

    if not df.empty and cve_id in df["cve_id"].values:
        # Update existing
        idx = df[df["cve_id"] == cve_id].index[0]
        for k, v in record.items():
            df.at[idx, k] = v
    else:
        # Append new
        new_row_df = pd.DataFrame([record])
        df = pd.concat([df, new_row_df], ignore_index=True)

    # Recalculate rankings
    clean_cvss = df["cvss_v3_score"].fillna(0.0)
    clean_risk = df["risk_score"].fillna(0.0)

    df["rank_cvss"] = clean_cvss.rank(ascending=False, method="min").astype(int)
    df["rank_contextual"] = clean_risk.rank(ascending=False, method="min").astype(int)
    df["rank_displacement"] = df["rank_cvss"] - df["rank_contextual"]
    df["in_kev"] = df["in_kev"].astype(bool)

    # Persist to SQLite if path provided
    if db_path is not None:
        try:
            from src.pipeline.database import Database
            db = Database(str(db_path))
            db.upsert_vulnerabilities(pd.DataFrame([record]))
            logger.info("Persisted custom CVE %s to SQLite database", cve_id)
        except Exception as exc:
            logger.error("Failed persisting custom CVE %s to SQLite: %s", cve_id, exc)

    updated_row = df[df["cve_id"] == cve_id].iloc[0]
    return df, updated_row
