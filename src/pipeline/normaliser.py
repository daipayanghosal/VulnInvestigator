"""
src/pipeline/normaliser.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Transforms raw API responses from NVD and CISA KEV into clean, typed
Pandas DataFrames, and merges them into a unified vulnerability dataset.

Design goals:
- All transformations are stateless (pure-ish methods, no side effects).
- Missing / null values are handled gracefully (NaN or empty string).
- Output schema is documented in docs/data_dictionary.md.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DataNormaliser:
    """Transforms raw pipeline data into clean, analysis-ready DataFrames.

    Usage
    -----
    >>> normaliser = DataNormaliser()
    >>> nvd_df = normaliser.normalise_nvd(raw_cves)
    >>> kev_df = normaliser.normalise_kev(raw_kev)
    >>> merged = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
    """

    # ------------------------------------------------------------------
    # NVD normalisation
    # ------------------------------------------------------------------

    def normalise_nvd(self, raw_cves: list[dict[str, Any]]) -> pd.DataFrame:
        """Normalise raw NVD CVE items into a flat DataFrame.

        Each item in ``raw_cves`` is expected to have the structure returned by
        the NVD CVE 2.0 API, i.e. ``{"cve": {...}}``.

        Output columns
        --------------
        cve_id, description, cvss_v3_score, cvss_v3_severity, cvss_v3_vector,
        published_date, last_modified, affected_products, references

        Parameters
        ----------
        raw_cves:
            List of raw NVD ``vulnerabilities`` items.

        Returns
        -------
        pd.DataFrame
        """
        records: list[dict[str, Any]] = []

        for item in raw_cves:
            cve: dict[str, Any] = item.get("cve", {})
            cve_id: str = cve.get("id", "")

            # --- Description (prefer English) ---
            descriptions = cve.get("descriptions", [])
            description = next(
                (d["value"] for d in descriptions if d.get("lang") == "en"), ""
            )

            # --- CVSS v3.x (prefer v3.1 over v3.0) ---
            metrics = cve.get("metrics", {})
            cvss_v3_score: float | None = None
            cvss_v3_severity: str = ""
            cvss_v3_vector: str = ""

            for key in ("cvssMetricV31", "cvssMetricV30"):
                metric_list = metrics.get(key, [])
                if metric_list:
                    primary = next(
                        (m for m in metric_list if m.get("type") == "Primary"),
                        metric_list[0],
                    )
                    cvss_data = primary.get("cvssData", {})
                    cvss_v3_score = cvss_data.get("baseScore")
                    cvss_v3_severity = cvss_data.get("baseSeverity", "")
                    cvss_v3_vector = cvss_data.get("vectorString", "")
                    break  # stop after first match

            # --- Dates ---
            published_date: str = cve.get("published", "")
            last_modified: str = cve.get("lastModified", "")

            # --- Affected products (CPE match strings) ---
            configs = cve.get("configurations", [])
            products: list[str] = []
            for config in configs:
                for node in config.get("nodes", []):
                    for cpe_match in node.get("cpeMatch", []):
                        cpe_name = cpe_match.get("criteria", "")
                        if cpe_name and cpe_name not in products:
                            products.append(cpe_name)
            affected_products: str = "; ".join(products)

            # --- References ---
            refs = cve.get("references", [])
            references: str = "; ".join(r.get("url", "") for r in refs if r.get("url"))

            records.append(
                {
                    "cve_id": cve_id,
                    "description": description,
                    "cvss_v3_score": cvss_v3_score,
                    "cvss_v3_severity": cvss_v3_severity,
                    "cvss_v3_vector": cvss_v3_vector,
                    "published_date": published_date,
                    "last_modified": last_modified,
                    "affected_products": affected_products,
                    "references": references,
                }
            )

        df = pd.DataFrame(records)
        if not df.empty:
            df["cvss_v3_score"] = pd.to_numeric(df["cvss_v3_score"], errors="coerce")
            df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce", utc=True)
            df["last_modified"] = pd.to_datetime(df["last_modified"], errors="coerce", utc=True)
        logger.info("NVD normalised: %d CVEs → DataFrame shape %s", len(raw_cves), df.shape)
        return df

    # ------------------------------------------------------------------
    # KEV normalisation
    # ------------------------------------------------------------------

    def normalise_kev(self, raw_kev: list[dict[str, Any]]) -> pd.DataFrame:
        """Normalise raw CISA KEV entries into a flat DataFrame.

        Output columns
        --------------
        cve_id, vendor_project, product, vulnerability_name,
        date_added, short_description, required_action, due_date

        Parameters
        ----------
        raw_kev:
            List of KEV dicts as returned by ``KEVClient.fetch()``.

        Returns
        -------
        pd.DataFrame
        """
        records: list[dict[str, Any]] = []
        for entry in raw_kev:
            records.append(
                {
                    "cve_id": entry.get("cveID", "").upper(),
                    "vendor_project": entry.get("vendorProject", ""),
                    "product": entry.get("product", ""),
                    "vulnerability_name": entry.get("vulnerabilityName", ""),
                    "date_added": entry.get("dateAdded", ""),
                    "short_description": entry.get("shortDescription", ""),
                    "required_action": entry.get("requiredAction", ""),
                    "due_date": entry.get("dueDate", ""),
                }
            )

        df = pd.DataFrame(records)
        if not df.empty:
            df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
            df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
        logger.info("KEV normalised: %d entries → DataFrame shape %s", len(raw_kev), df.shape)
        return df

    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------

    def merge_vulnerability_dataset(
        self, nvd_df: pd.DataFrame, kev_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Left-join NVD CVEs with the KEV catalogue and add an ``in_kev`` flag.

        All NVD CVEs are retained; those with a matching entry in KEV have
        ``in_kev = True`` and the KEV metadata columns populated.

        Parameters
        ----------
        nvd_df:
            Output of :meth:`normalise_nvd`.
        kev_df:
            Output of :meth:`normalise_kev`.

        Returns
        -------
        pd.DataFrame
            Merged DataFrame with ``in_kev`` boolean column.
        """
        kev_cols = [
            "cve_id",
            "vendor_project",
            "product",
            "vulnerability_name",
            "date_added",
            "short_description",
            "required_action",
            "due_date",
        ]
        # Only keep the extra KEV columns (avoid duplicating cve_id)
        kev_merge = kev_df[kev_cols].copy() if not kev_df.empty else pd.DataFrame(columns=kev_cols)

        merged = nvd_df.merge(kev_merge, on="cve_id", how="left", suffixes=("", "_kev"))
        merged["in_kev"] = merged["cve_id"].isin(
            set(kev_df["cve_id"].str.upper()) if not kev_df.empty else set()
        )
        logger.info(
            "Merge complete: %d total CVEs, %d in KEV",
            len(merged),
            merged["in_kev"].sum(),
        )
        return merged

    # ------------------------------------------------------------------
    # I/O helpers
    # ------------------------------------------------------------------

    def save_parquet(self, df: pd.DataFrame, path: str) -> None:
        """Save a DataFrame to Parquet format (requires PyArrow).

        Parameters
        ----------
        df: DataFrame to save.
        path: Destination file path.
        """
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(dest, index=False, engine="pyarrow")
        logger.info("Saved DataFrame (%d rows) → %s", len(df), dest)

    def load_parquet(self, path: str) -> pd.DataFrame:
        """Load a DataFrame from a Parquet file.

        Parameters
        ----------
        path: Source file path.

        Returns
        -------
        pd.DataFrame
        """
        df = pd.read_parquet(path, engine="pyarrow")
        logger.info("Loaded DataFrame (%d rows) ← %s", len(df), path)
        return df
