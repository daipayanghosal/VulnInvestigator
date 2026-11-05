"""
tests/test_pipeline.py
~~~~~~~~~~~~~~~~~~~~~~~
Pytest tests for DataNormaliser.

Tests cover:
- NVD normalisation produces expected columns
- KEV normalisation produces expected columns
- Merge adds in_kev flag correctly
- Empty inputs handled gracefully
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.pipeline.normaliser import DataNormaliser


# ---------------------------------------------------------------------------
# Helpers / sample data
# ---------------------------------------------------------------------------

def _make_raw_nvd_item(
    cve_id: str = "CVE-2024-1234",
    score: float = 9.8,
    description: str = "Test vulnerability",
) -> dict:
    """Minimal valid NVD CVE 2.0 API item structure."""
    return {
        "cve": {
            "id": cve_id,
            "published": "2024-01-15T00:00:00.000",
            "lastModified": "2024-02-01T00:00:00.000",
            "descriptions": [{"lang": "en", "value": description}],
            "metrics": {
                "cvssMetricV31": [
                    {
                        "type": "Primary",
                        "cvssData": {
                            "baseScore": score,
                            "baseSeverity": "CRITICAL",
                            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                        },
                    }
                ]
            },
            "configurations": [
                {
                    "nodes": [
                        {
                            "cpeMatch": [
                                {"criteria": "cpe:2.3:a:apache:http_server:2.4.58:*:*:*:*:*:*:*"}
                            ]
                        }
                    ]
                }
            ],
            "references": [{"url": "https://example.com/advisory"}],
        }
    }


def _make_raw_kev_item(cve_id: str = "CVE-2024-1234") -> dict:
    return {
        "cveID": cve_id,
        "vendorProject": "Apache",
        "product": "HTTP Server",
        "vulnerabilityName": "Apache Test Vuln",
        "dateAdded": "2024-01-20",
        "shortDescription": "Short desc",
        "requiredAction": "Apply patch",
        "dueDate": "2024-02-10",
    }


@pytest.fixture()
def normaliser() -> DataNormaliser:
    return DataNormaliser()


@pytest.fixture()
def sample_raw_nvd() -> list[dict]:
    return [
        _make_raw_nvd_item("CVE-2024-0001", 9.8),
        _make_raw_nvd_item("CVE-2024-0002", 7.5),
        _make_raw_nvd_item("CVE-2024-0003", 5.0),
    ]


@pytest.fixture()
def sample_raw_kev() -> list[dict]:
    return [_make_raw_kev_item("CVE-2024-0001")]


# ---------------------------------------------------------------------------
# NVD normalisation tests
# ---------------------------------------------------------------------------

class TestNormaliseNVD:

    def test_expected_columns(self, normaliser: DataNormaliser, sample_raw_nvd: list[dict]) -> None:
        df = normaliser.normalise_nvd(sample_raw_nvd)
        expected = {
            "cve_id", "description", "cvss_v3_score", "cvss_v3_severity",
            "cvss_v3_vector", "published_date", "last_modified",
            "affected_products", "references",
        }
        assert expected.issubset(set(df.columns))

    def test_row_count(self, normaliser: DataNormaliser, sample_raw_nvd: list[dict]) -> None:
        df = normaliser.normalise_nvd(sample_raw_nvd)
        assert len(df) == len(sample_raw_nvd)

    def test_cve_ids_extracted(self, normaliser: DataNormaliser, sample_raw_nvd: list[dict]) -> None:
        df = normaliser.normalise_nvd(sample_raw_nvd)
        assert set(df["cve_id"].tolist()) == {"CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"}

    def test_cvss_score_numeric(self, normaliser: DataNormaliser, sample_raw_nvd: list[dict]) -> None:
        df = normaliser.normalise_nvd(sample_raw_nvd)
        assert pd.api.types.is_float_dtype(df["cvss_v3_score"])

    def test_description_extracted(self, normaliser: DataNormaliser) -> None:
        item = _make_raw_nvd_item(description="A specific test description.")
        df = normaliser.normalise_nvd([item])
        assert df["description"].iloc[0] == "A specific test description."

    def test_no_cvss_returns_nan(self, normaliser: DataNormaliser) -> None:
        item = {
            "cve": {
                "id": "CVE-2024-9999",
                "published": "",
                "lastModified": "",
                "descriptions": [{"lang": "en", "value": "No CVSS"}],
                "metrics": {},
                "configurations": [],
                "references": [],
            }
        }
        df = normaliser.normalise_nvd([item])
        assert pd.isna(df["cvss_v3_score"].iloc[0])

    def test_empty_input(self, normaliser: DataNormaliser) -> None:
        df = normaliser.normalise_nvd([])
        assert df.empty


# ---------------------------------------------------------------------------
# KEV normalisation tests
# ---------------------------------------------------------------------------

class TestNormaliseKEV:

    def test_expected_columns(self, normaliser: DataNormaliser, sample_raw_kev: list[dict]) -> None:
        df = normaliser.normalise_kev(sample_raw_kev)
        expected = {
            "cve_id", "vendor_project", "product", "vulnerability_name",
            "date_added", "short_description", "required_action", "due_date",
        }
        assert expected.issubset(set(df.columns))

    def test_cve_id_uppercased(self, normaliser: DataNormaliser) -> None:
        df = normaliser.normalise_kev([_make_raw_kev_item("cve-2024-9999")])
        assert df["cve_id"].iloc[0] == "CVE-2024-9999"

    def test_empty_input(self, normaliser: DataNormaliser) -> None:
        df = normaliser.normalise_kev([])
        assert df.empty


# ---------------------------------------------------------------------------
# Merge tests
# ---------------------------------------------------------------------------

class TestMergeVulnerabilityDataset:

    def test_in_kev_flag_set(
        self,
        normaliser: DataNormaliser,
        sample_raw_nvd: list[dict],
        sample_raw_kev: list[dict],
    ) -> None:
        nvd_df = normaliser.normalise_nvd(sample_raw_nvd)
        kev_df = normaliser.normalise_kev(sample_raw_kev)
        merged = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
        kev_row = merged[merged["cve_id"] == "CVE-2024-0001"]
        non_kev_row = merged[merged["cve_id"] == "CVE-2024-0002"]
        assert bool(kev_row["in_kev"].iloc[0]) is True
        assert bool(non_kev_row["in_kev"].iloc[0]) is False

    def test_all_nvd_rows_retained(
        self,
        normaliser: DataNormaliser,
        sample_raw_nvd: list[dict],
        sample_raw_kev: list[dict],
    ) -> None:
        nvd_df = normaliser.normalise_nvd(sample_raw_nvd)
        kev_df = normaliser.normalise_kev(sample_raw_kev)
        merged = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
        assert len(merged) == len(sample_raw_nvd), "All NVD rows must be retained (left join)"

    def test_in_kev_column_exists(
        self,
        normaliser: DataNormaliser,
        sample_raw_nvd: list[dict],
        sample_raw_kev: list[dict],
    ) -> None:
        nvd_df = normaliser.normalise_nvd(sample_raw_nvd)
        kev_df = normaliser.normalise_kev(sample_raw_kev)
        merged = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
        assert "in_kev" in merged.columns

    def test_empty_kev(self, normaliser: DataNormaliser, sample_raw_nvd: list[dict]) -> None:
        nvd_df = normaliser.normalise_nvd(sample_raw_nvd)
        kev_df = normaliser.normalise_kev([])
        merged = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
        assert merged["in_kev"].sum() == 0
