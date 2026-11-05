"""
tests/test_custom_cve.py
~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for custom CVE manual ingestion and scoring helpers.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.pipeline.custom_cve import (
    is_valid_cve_id,
    calculate_custom_risk,
    ingest_custom_cve,
)


def test_is_valid_cve_id():
    assert is_valid_cve_id("CVE-2024-3400") is True
    assert is_valid_cve_id("cve-2023-123456") is True
    assert is_valid_cve_id("INVALID-123") is False
    assert is_valid_cve_id("") is False


def test_calculate_custom_risk():
    # Asset is critical and internet-facing
    asset = {"criticality": "critical", "exposure": "internet_facing"}
    score, band = calculate_custom_risk(cvss_score=10.0, in_kev=True, asset=asset)
    assert 0.95 <= score <= 1.0
    assert band == "Critical"

    # Asset is internal and low criticality, not in KEV
    asset_low = {"criticality": "low", "exposure": "internal"}
    score_low, band_low = calculate_custom_risk(cvss_score=4.0, in_kev=False, asset=asset_low)
    assert score_low < 0.40
    assert band_low == "Low"


def test_ingest_custom_cve(tmp_path):
    existing_df = pd.DataFrame([
        {
            "cve_id": "CVE-2023-0001",
            "cvss_v3_score": 7.0,
            "risk_score": 0.50,
            "in_kev": False,
        }
    ])

    custom_data = {
        "cve_id": "CVE-2024-9999",
        "cvss_v3_score": 9.8,
        "cvss_v3_severity": "CRITICAL",
        "in_kev": True,
        "risk_score": 0.95,
        "risk_band": "Critical",
        "description": "Zero-day remote code execution",
        "affected_products": "Vendor Product 1.0",
        "matched_asset_id": "SRV-WEB-001",
    }

    test_db = tmp_path / "test.db"
    updated_df, new_row = ingest_custom_cve(existing_df, custom_data, db_path=test_db)

    assert len(updated_df) == 2
    assert "CVE-2024-9999" in updated_df["cve_id"].values
    assert new_row["cve_id"] == "CVE-2024-9999"
    assert new_row["rank_contextual"] == 1  # 0.95 > 0.50
    assert new_row["rank_cvss"] == 1        # 9.8 > 7.0
    assert test_db.exists()
