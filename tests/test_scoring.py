"""
tests/test_scoring.py
~~~~~~~~~~~~~~~~~~~~~
Pytest tests for CVSSBaselineScorer and ContextualRiskScorer.

Tests cover:
- Correct score computation and ordering
- Risk band assignment
- Missing CVSS values handled gracefully
- Weights validation (must sum to 1.0)
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.scoring.baseline import CVSSBaselineScorer
from src.scoring.contextual import ContextualRiskScorer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_vuln_df() -> pd.DataFrame:
    """A minimal vulnerability DataFrame for testing."""
    return pd.DataFrame(
        {
            "cve_id": ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003", "CVE-2024-0004"],
            "cvss_v3_score": [9.8, 7.5, 5.0, None],
            "cvss_v3_severity": ["CRITICAL", "HIGH", "MEDIUM", None],
            "in_kev": [True, False, False, False],
            "affected_products": [
                "cpe:2.3:a:apache:http_server:2.4.58:*",
                "cpe:2.3:a:microsoft:windows_10:*",
                "cpe:2.3:a:openssl:openssl:3.1.4:*",
                "cpe:2.3:a:unknown:unknown:1.0:*",
            ],
        }
    )


@pytest.fixture()
def sample_assets() -> list[dict]:
    return [
        {
            "asset_id": "SRV-WEB-001",
            "hostname": "web-01",
            "software": ["Apache HTTP Server 2.4.58", "OpenSSL 3.1.4"],
            "criticality": "critical",
            "exposure": "internet_facing",
        },
        {
            "asset_id": "WS-DEV-001",
            "hostname": "dev-laptop",
            "software": ["Python 3.12", "Git 2.44"],
            "criticality": "medium",
            "exposure": "internal",
        },
    ]


@pytest.fixture()
def contextual_scorer() -> ContextualRiskScorer:
    return ContextualRiskScorer()


# ---------------------------------------------------------------------------
# CVSSBaselineScorer tests
# ---------------------------------------------------------------------------

class TestCVSSBaselineScorer:

    def test_scores_sorted_descending(self, sample_vuln_df: pd.DataFrame) -> None:
        scorer = CVSSBaselineScorer()
        result = scorer.score(sample_vuln_df)
        scores = result["cvss_v3_score"].dropna().tolist()
        assert scores == sorted(scores, reverse=True), "Scores should be descending"

    def test_rank_column_added(self, sample_vuln_df: pd.DataFrame) -> None:
        scorer = CVSSBaselineScorer()
        result = scorer.score(sample_vuln_df)
        assert "rank_cvss" in result.columns

    def test_rank_starts_at_one(self, sample_vuln_df: pd.DataFrame) -> None:
        scorer = CVSSBaselineScorer()
        result = scorer.score(sample_vuln_df)
        assert result["rank_cvss"].iloc[0] == 1

    def test_missing_cvss_sorted_last(self, sample_vuln_df: pd.DataFrame) -> None:
        scorer = CVSSBaselineScorer()
        result = scorer.score(sample_vuln_df)
        # Row with None cvss should be last
        assert pd.isna(result["cvss_v3_score"].iloc[-1])

    def test_top_n_returns_correct_count(self, sample_vuln_df: pd.DataFrame) -> None:
        scorer = CVSSBaselineScorer(sample_vuln_df)
        top2 = scorer.get_top_n(2)
        assert len(top2) == 2

    def test_get_top_n_before_score_raises(self) -> None:
        scorer = CVSSBaselineScorer()
        with pytest.raises(RuntimeError):
            scorer.get_top_n(5)

    def test_empty_dataframe(self) -> None:
        scorer = CVSSBaselineScorer()
        result = scorer.score(pd.DataFrame(columns=["cve_id", "cvss_v3_score"]))
        assert result.empty

    def test_missing_column_raises(self) -> None:
        scorer = CVSSBaselineScorer()
        with pytest.raises(ValueError):
            scorer.score(pd.DataFrame({"cve_id": ["CVE-X"]}))


# ---------------------------------------------------------------------------
# ContextualRiskScorer tests
# ---------------------------------------------------------------------------

class TestContextualRiskScorer:

    def test_weights_must_sum_to_one(self) -> None:
        with pytest.raises(ValueError, match="sum to 1.0"):
            ContextualRiskScorer(weights_config={"cvss": 0.5, "kev": 0.5, "asset_criticality": 0.5, "exposure": 0.5})

    def test_valid_score_range(
        self,
        contextual_scorer: ContextualRiskScorer,
        sample_vuln_df: pd.DataFrame,
        sample_assets: list[dict],
    ) -> None:
        result = contextual_scorer.score_dataframe(sample_vuln_df, sample_assets)
        assert result["risk_score"].between(0.0, 1.0).all(), "All scores should be in [0, 1]"

    def test_kev_increases_score(self, contextual_scorer: ContextualRiskScorer) -> None:
        base_row = pd.Series({"cvss_v3_score": 7.5, "in_kev": False})
        kev_row = pd.Series({"cvss_v3_score": 7.5, "in_kev": True})
        asset = {"criticality": "medium", "exposure": "internal"}
        base_score = contextual_scorer.score_vulnerability(base_row, asset)
        kev_score = contextual_scorer.score_vulnerability(kev_row, asset)
        assert kev_score > base_score, "KEV flag should increase the risk score"

    def test_missing_cvss_handled(self, contextual_scorer: ContextualRiskScorer) -> None:
        row = pd.Series({"cvss_v3_score": None, "in_kev": False})
        asset = {"criticality": "low", "exposure": "internal"}
        score = contextual_scorer.score_vulnerability(row, asset)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_missing_asset_handled(self, contextual_scorer: ContextualRiskScorer) -> None:
        row = pd.Series({"cvss_v3_score": 8.0, "in_kev": True})
        score = contextual_scorer.score_vulnerability(row, asset=None)
        assert isinstance(score, float)

    def test_risk_band_critical(self, contextual_scorer: ContextualRiskScorer) -> None:
        assert contextual_scorer.get_risk_band(0.90) == "Critical"

    def test_risk_band_high(self, contextual_scorer: ContextualRiskScorer) -> None:
        assert contextual_scorer.get_risk_band(0.70) == "High"

    def test_risk_band_medium(self, contextual_scorer: ContextualRiskScorer) -> None:
        assert contextual_scorer.get_risk_band(0.50) == "Medium"

    def test_risk_band_low(self, contextual_scorer: ContextualRiskScorer) -> None:
        assert contextual_scorer.get_risk_band(0.20) == "Low"

    def test_rank_contextual_column_added(
        self,
        contextual_scorer: ContextualRiskScorer,
        sample_vuln_df: pd.DataFrame,
        sample_assets: list[dict],
    ) -> None:
        result = contextual_scorer.score_dataframe(sample_vuln_df, sample_assets)
        assert "rank_contextual" in result.columns

    def test_critical_asset_internet_facing_scores_higher(
        self, contextual_scorer: ContextualRiskScorer
    ) -> None:
        row = pd.Series({"cvss_v3_score": 7.0, "in_kev": False})
        critical_asset = {"criticality": "critical", "exposure": "internet_facing"}
        low_asset = {"criticality": "low", "exposure": "air_gapped"}
        high_score = contextual_scorer.score_vulnerability(row, critical_asset)
        low_score = contextual_scorer.score_vulnerability(row, low_asset)
        assert high_score > low_score
