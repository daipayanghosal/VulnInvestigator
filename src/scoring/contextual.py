"""
src/scoring/contextual.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Contextual risk scorer that augments CVSS with KEV exploitation status,
asset criticality, and network exposure.

Formula
-------
    risk_score = w_cvss  * (cvss_v3_score / 10.0)
               + w_kev   * kev_flag          (1.0 if in KEV, else 0.0)
               + w_asset * asset_criticality  (0.0 – 1.0)
               + w_exp   * exposure_score     (0.0 – 1.0)

Weights are loaded from ``config/scoring.yaml`` and must sum to 1.0.
The final score is clamped to [0.0, 1.0].
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Default weight config (mirrors config/scoring.yaml)
_DEFAULT_WEIGHTS = {"cvss": 0.35, "kev": 0.30, "asset_criticality": 0.20, "exposure": 0.15}
_DEFAULT_CRITICALITY = {"critical": 1.0, "high": 0.75, "medium": 0.50, "low": 0.25, "unknown": 0.10}
_DEFAULT_EXPOSURE = {
    "internet_facing": 1.0, "dmz": 0.75, "internal": 0.50, "restricted": 0.25, "air_gapped": 0.0
}
_DEFAULT_BANDS = {"critical": 0.80, "high": 0.60, "medium": 0.40, "low": 0.0}


class ContextualRiskScorer:
    """Scores vulnerabilities using a weighted, multi-factor formula.

    Parameters
    ----------
    weights_config:
        Dict with keys ``cvss``, ``kev``, ``asset_criticality``, ``exposure``
        mapping to floats that sum to 1.0.
    asset_config:
        Dict mapping asset criticality tier strings to scores (0–1).
    exposure_config:
        Dict mapping exposure tier strings to scores (0–1).
    bands_config:
        Dict mapping band label to minimum score threshold.
    """

    def __init__(
        self,
        weights_config: dict[str, float] | None = None,
        asset_config: dict[str, float] | None = None,
        exposure_config: dict[str, float] | None = None,
        bands_config: dict[str, float] | None = None,
    ) -> None:
        self.weights = weights_config or _DEFAULT_WEIGHTS
        self.asset_criticality_map = asset_config or _DEFAULT_CRITICALITY
        self.exposure_map = exposure_config or _DEFAULT_EXPOSURE
        self.bands = bands_config or _DEFAULT_BANDS

        # Validate weights
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"ContextualRiskScorer: weights must sum to 1.0, got {total:.4f}"
            )
        logger.info("ContextualRiskScorer initialised (weights=%s)", self.weights)

    # ------------------------------------------------------------------
    # Single-row scoring
    # ------------------------------------------------------------------

    def score_vulnerability(
        self, row: pd.Series, asset: dict[str, Any] | None
    ) -> float:
        """Compute the contextual risk score for one CVE / asset pairing.

        Parameters
        ----------
        row:
            A row from the merged vulnerability DataFrame.  Expected fields:
            ``cvss_v3_score`` (float | NaN) and ``in_kev`` (bool | int).
        asset:
            Asset dict (from ``AssetInventory``), or ``None`` if no asset is matched.
            Used to look up ``criticality`` and ``exposure`` tiers.

        Returns
        -------
        float
            Contextual risk score in [0.0, 1.0].
        """
        w = self.weights

        # 1. CVSS normalised to [0, 1]
        raw_cvss = row.get("cvss_v3_score", None)
        if pd.isna(raw_cvss) or raw_cvss is None:
            cvss_norm = 0.0
        else:
            cvss_norm = float(raw_cvss) / 10.0

        # 2. KEV flag (binary)
        in_kev_raw = row.get("in_kev", False)
        kev_flag = 1.0 if bool(in_kev_raw) else 0.0

        # 3. Asset criticality
        if asset:
            crit_tier = asset.get("criticality", "unknown").lower()
            asset_crit = self.asset_criticality_map.get(
                crit_tier, self.asset_criticality_map.get("unknown", 0.10)
            )
            # 4. Exposure
            exp_tier = asset.get("exposure", "internal").lower()
            exposure = self.exposure_map.get(exp_tier, self.exposure_map.get("internal", 0.50))
        else:
            # No matched asset — use conservative defaults
            asset_crit = self.asset_criticality_map.get("unknown", 0.10)
            exposure = self.exposure_map.get("internal", 0.50)

        score = (
            w.get("cvss", 0.35) * cvss_norm
            + w.get("kev", 0.30) * kev_flag
            + w.get("asset_criticality", 0.20) * asset_crit
            + w.get("exposure", 0.15) * exposure
        )

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------------
    # DataFrame scoring
    # ------------------------------------------------------------------

    def score_dataframe(
        self,
        vuln_df: pd.DataFrame,
        asset_inventory: list[dict[str, Any]],
    ) -> pd.DataFrame:
        """Apply contextual scoring to every row in *vuln_df*.

        For each CVE, finds the first asset whose ``software`` list contains
        a keyword from ``affected_products`` (case-insensitive substring match).

        Adds columns
        ------------
        ``risk_score``        : float in [0.0, 1.0]
        ``risk_band``         : str — "Critical" | "High" | "Medium" | "Low"
        ``matched_asset_id``  : str | "" — ID of the matched asset

        Parameters
        ----------
        vuln_df:
            Merged vulnerability DataFrame.
        asset_inventory:
            List of asset dicts (from ``AssetInventory.load()``).

        Returns
        -------
        pd.DataFrame
            *vuln_df* copy with the three new columns, sorted descending by
            ``risk_score`` with a ``rank_contextual`` column prepended.
        """
        if vuln_df.empty:
            logger.warning("ContextualRiskScorer.score_dataframe: empty DataFrame")
            return vuln_df.copy()

        # Build product→asset lookup for fast matching
        # Key: lowercase software string fragment; value: asset dict
        scored_rows: list[dict[str, Any]] = []

        for _, row in vuln_df.iterrows():
            matched_asset: dict[str, Any] | None = None
            matched_id: str = ""

            affected = str(row.get("affected_products", "") or "")
            if affected:
                # Try to match keywords from CPE / product strings against asset software lists
                # We extract simple vendor/product tokens from CPE strings
                keywords = _extract_keywords_from_products(affected)
                for asset in asset_inventory:
                    asset_sw = " ".join(asset.get("software", [])).lower()
                    if any(kw in asset_sw for kw in keywords):
                        matched_asset = asset
                        matched_id = asset.get("asset_id", "")
                        break

            risk = self.score_vulnerability(row, matched_asset)
            scored_rows.append(
                {
                    **row.to_dict(),
                    "risk_score": risk,
                    "risk_band": self.get_risk_band(risk),
                    "matched_asset_id": matched_id,
                }
            )

        result = pd.DataFrame(scored_rows)
        result = result.sort_values("risk_score", ascending=False, na_position="last")
        result = result.reset_index(drop=True)
        if "rank_contextual" in result.columns:
            result = result.drop(columns=["rank_contextual"])
        result.insert(0, "rank_contextual", range(1, len(result) + 1))

        logger.info(
            "ContextualRiskScorer: scored %d CVEs; top risk_score=%.3f",
            len(result),
            result["risk_score"].iloc[0] if not result.empty else float("nan"),
        )
        return result

    # ------------------------------------------------------------------
    # Band lookup
    # ------------------------------------------------------------------

    def get_risk_band(self, score: float) -> str:
        """Classify a numeric risk score into a labelled band.

        Parameters
        ----------
        score:
            Numeric risk score in [0.0, 1.0].

        Returns
        -------
        str
            One of ``"Critical"``, ``"High"``, ``"Medium"``, ``"Low"``.
        """
        # Bands are defined as minimum thresholds; iterate in descending order
        for label in ("critical", "high", "medium", "low"):
            threshold = self.bands.get(label, 0.0)
            if score >= threshold:
                return label.capitalize()
        return "Low"


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_keywords_from_products(affected_products: str) -> list[str]:
    """Extract simple lowercase keywords from a semicolon-separated CPE string.

    CPE URIs look like ``cpe:2.3:a:apache:http_server:2.4.58:*…``.
    We extract the vendor and product components and clean underscores.

    Parameters
    ----------
    affected_products:
        Semicolon-separated CPE match criteria string.

    Returns
    -------
    list[str]
        Lowercase keyword list; empty strings are filtered out.
    """
    keywords: list[str] = []
    for part in affected_products.split(";"):
        part = part.strip()
        if not part:
            continue
        # CPE 2.3 format: cpe:2.3:<type>:<vendor>:<product>:<version>:...
        segments = part.split(":")
        # indices 3=vendor, 4=product in CPE 2.3
        for idx in (3, 4):
            if idx < len(segments):
                token = segments[idx].replace("_", " ").replace("-", " ").lower()
                if token and token != "*":
                    keywords.append(token)
    return list(set(keywords))  # deduplicate
