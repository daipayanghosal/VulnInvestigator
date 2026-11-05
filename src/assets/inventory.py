"""
src/assets/inventory.py
~~~~~~~~~~~~~~~~~~~~~~~
Asset inventory loader and query interface.

Loads the JSON asset inventory (``data/assets/asset_inventory.json``) and
provides helpers used by the scoring and correlation modules to look up
asset metadata, criticality tier, and network exposure tier.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

# Default scoring config path (resolved relative to project root)
_DEFAULT_SCORING_CONFIG = Path(__file__).resolve().parents[2] / "config" / "scoring.yaml"


class AssetInventory:
    """Loads and queries the organisation asset inventory.

    Parameters
    ----------
    scoring_config_path:
        Path to ``config/scoring.yaml`` for criticality/exposure tier lookups.
        Defaults to the standard project location.
    """

    def __init__(self, scoring_config_path: str | Path = _DEFAULT_SCORING_CONFIG) -> None:
        self._assets: list[dict[str, Any]] = []
        self._index: dict[str, dict[str, Any]] = {}  # asset_id → asset

        # Load scoring config for tier → float lookups
        config_path = Path(scoring_config_path)
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as fh:
                scoring_cfg = yaml.safe_load(fh)
            self._criticality_map: dict[str, float] = scoring_cfg.get("asset_criticality", {})
            self._exposure_map: dict[str, float] = scoring_cfg.get("exposure", {})
        else:
            logger.warning("Scoring config not found at %s; using defaults", config_path)
            self._criticality_map = {
                "critical": 1.0, "high": 0.75, "medium": 0.50, "low": 0.25, "unknown": 0.10
            }
            self._exposure_map = {
                "internet_facing": 1.0, "dmz": 0.75,
                "internal": 0.50, "restricted": 0.25, "air_gapped": 0.0,
            }

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, path: str) -> list[dict[str, Any]]:
        """Load the JSON asset inventory from *path*.

        Parameters
        ----------
        path:
            Absolute or relative path to ``asset_inventory.json``.

        Returns
        -------
        list[dict]
            List of asset dicts.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        src = Path(path)
        if not src.exists():
            raise FileNotFoundError(f"Asset inventory not found: {src}")

        with src.open("r", encoding="utf-8") as fh:
            payload: dict[str, Any] = json.load(fh)

        self._assets = payload.get("assets", [])
        self._index = {a["asset_id"]: a for a in self._assets if "asset_id" in a}
        logger.info(
            "AssetInventory: loaded %d assets from %s (org: %s)",
            len(self._assets),
            src,
            payload.get("organisation", "unknown"),
        )
        return self._assets

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        """Return the asset dict for *asset_id*, or ``None`` if not found.

        Parameters
        ----------
        asset_id: Exact asset ID string.
        """
        return self._index.get(asset_id)

    def get_assets_by_product(self, product_name: str) -> list[dict[str, Any]]:
        """Return all assets whose ``software`` list contains *product_name*.

        The match is case-insensitive substring matching.

        Parameters
        ----------
        product_name:
            Product string to search for, e.g. ``"Apache HTTP Server"``.

        Returns
        -------
        list[dict]
        """
        needle = product_name.lower()
        matches: list[dict[str, Any]] = []
        for asset in self._assets:
            software_list = asset.get("software", [])
            if any(needle in sw.lower() for sw in software_list):
                matches.append(asset)
        return matches

    def get_criticality_score(self, asset_id: str) -> float:
        """Return the numeric criticality score (0–1) for *asset_id*.

        Falls back to the ``"unknown"`` tier (0.10) if the asset is not found
        or has an unrecognised criticality label.

        Parameters
        ----------
        asset_id: Asset identifier.
        """
        asset = self._index.get(asset_id)
        if not asset:
            return self._criticality_map.get("unknown", 0.10)
        tier = asset.get("criticality", "unknown").lower()
        return self._criticality_map.get(tier, self._criticality_map.get("unknown", 0.10))

    def get_exposure_score(self, asset_id: str) -> float:
        """Return the numeric exposure score (0–1) for *asset_id*.

        Falls back to 0.50 (``"internal"`` tier) if the asset is not found
        or has an unrecognised exposure label.

        Parameters
        ----------
        asset_id: Asset identifier.
        """
        asset = self._index.get(asset_id)
        if not asset:
            return self._exposure_map.get("internal", 0.50)
        tier = asset.get("exposure", "internal").lower()
        return self._exposure_map.get(tier, self._exposure_map.get("internal", 0.50))

    def to_dataframe(self) -> pd.DataFrame:
        """Return the full asset inventory as a Pandas DataFrame.

        List-valued columns (``software``, ``tags``) are serialised as
        pipe-separated strings for compatibility with Parquet / SQLite.

        Returns
        -------
        pd.DataFrame
        """
        records: list[dict[str, Any]] = []
        for asset in self._assets:
            row = dict(asset)
            row["software"] = "|".join(asset.get("software", []))
            row["tags"] = "|".join(asset.get("tags", []))
            records.append(row)
        df = pd.DataFrame(records)
        logger.debug("AssetInventory.to_dataframe: shape=%s", df.shape)
        return df
