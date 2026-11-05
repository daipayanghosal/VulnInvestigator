"""
tests/test_genai.py
~~~~~~~~~~~~~~~~~~~~~
Pytest tests for PromptBuilder and OutputValidator.

No real API calls are made — LLM responses are mocked.
"""

from __future__ import annotations

import pytest

from src.genai.prompt_builder import PromptBuilder
from src.genai.output_validator import OutputValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def builder() -> PromptBuilder:
    return PromptBuilder()


@pytest.fixture()
def validator() -> OutputValidator:
    return OutputValidator()


@pytest.fixture()
def sample_cve() -> dict:
    return {
        "cve_id": "CVE-2024-12345",
        "description": "A critical remote code execution vulnerability in Apache HTTP Server.",
        "cvss_v3_score": 9.8,
        "cvss_v3_severity": "CRITICAL",
        "in_kev": True,
        "affected_products": "cpe:2.3:a:apache:http_server:2.4.58:*",
        "references": "https://nvd.nist.gov/vuln/detail/CVE-2024-12345",
    }


@pytest.fixture()
def sample_asset() -> dict:
    return {
        "asset_id": "SRV-WEB-001",
        "hostname": "web-proxy-01",
        "os": "Ubuntu 22.04 LTS",
        "software": ["Apache HTTP Server 2.4.58", "OpenSSL 3.1.4"],
        "criticality": "critical",
        "exposure": "internet_facing",
        "notes": "Public-facing reverse proxy",
    }


@pytest.fixture()
def sample_scenario(sample_cve: dict, sample_asset: dict) -> dict:
    return {
        "cve_id": "CVE-2024-12345",
        "asset": sample_asset,
        "matched_techniques": [
            {
                "id": "T1190",
                "name": "Exploit Public-Facing Application",
                "description": "Adversaries may attempt to exploit weakness in an Internet-facing host.",
                "tactics": "initial-access",
            }
        ],
        "relevant_logs": [
            {
                "event_id": "evt-001",
                "timestamp": "2026-01-15T10:00:00+00:00",
                "asset_id": "SRV-WEB-001",
                "source_ip": "203.0.113.99",
                "event_type": "web_exploit_attempt",
                "technique_id": "T1190",
                "description": "Exploit payload detected in POST body",
                "raw_log": "src=203.0.113.99 method=POST uri=/admin status=200",
                "is_noise": False,
            }
        ],
        "evidence_summary": "CVE-2024-12345 affects SRV-WEB-001 running Apache 2.4.58.",
    }


@pytest.fixture()
def sample_evidence_bundle(sample_scenario: dict) -> dict:
    return sample_scenario


# ---------------------------------------------------------------------------
# PromptBuilder tests
# ---------------------------------------------------------------------------

class TestPromptBuilder:

    def test_ranking_prompt_returns_tuple(self, builder: PromptBuilder, sample_cve: dict) -> None:
        result = builder.build_ranking_explanation_prompt(sample_cve, {"risk_score": 0.92, "risk_band": "Critical", "matched_asset_id": "SRV-WEB-001"})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_ranking_prompt_contains_cve_id(self, builder: PromptBuilder, sample_cve: dict) -> None:
        _, user_prompt = builder.build_ranking_explanation_prompt(sample_cve, {"risk_score": 0.92, "risk_band": "Critical", "matched_asset_id": ""})
        assert "CVE-2024-12345" in user_prompt

    def test_ranking_prompt_contains_cvss(self, builder: PromptBuilder, sample_cve: dict) -> None:
        _, user_prompt = builder.build_ranking_explanation_prompt(sample_cve, {"risk_score": 0.92, "risk_band": "Critical", "matched_asset_id": ""})
        assert "9.8" in user_prompt

    def test_ranking_prompt_mentions_kev(self, builder: PromptBuilder, sample_cve: dict) -> None:
        _, user_prompt = builder.build_ranking_explanation_prompt(sample_cve, {"risk_score": 0.92, "risk_band": "Critical", "matched_asset_id": ""})
        assert "KEV" in user_prompt or "actively exploited" in user_prompt.lower()

    def test_investigation_prompt_has_all_sections(self, builder: PromptBuilder, sample_scenario: dict) -> None:
        _, user_prompt = builder.build_investigation_prompt(sample_scenario)
        sections = ["Section 1", "Section 2", "Section 3", "Section 4", "Section 5"]
        for section in sections:
            assert section in user_prompt, f"Missing section: {section}"

    def test_investigation_prompt_includes_log_event(self, builder: PromptBuilder, sample_scenario: dict) -> None:
        _, user_prompt = builder.build_investigation_prompt(sample_scenario)
        assert "evt-001" in user_prompt

    def test_investigation_prompt_includes_technique(self, builder: PromptBuilder, sample_scenario: dict) -> None:
        _, user_prompt = builder.build_investigation_prompt(sample_scenario)
        assert "T1190" in user_prompt

    def test_remediation_prompt_includes_cve_id(self, builder: PromptBuilder, sample_cve: dict, sample_asset: dict) -> None:
        _, user_prompt = builder.build_remediation_prompt(sample_cve, sample_asset)
        assert "CVE-2024-12345" in user_prompt

    def test_remediation_prompt_includes_asset_id(self, builder: PromptBuilder, sample_cve: dict, sample_asset: dict) -> None:
        _, user_prompt = builder.build_remediation_prompt(sample_cve, sample_asset)
        assert "SRV-WEB-001" in user_prompt

    def test_remediation_prompt_has_sections(self, builder: PromptBuilder, sample_cve: dict, sample_asset: dict) -> None:
        _, user_prompt = builder.build_remediation_prompt(sample_cve, sample_asset)
        assert "Immediate Actions" in user_prompt
        assert "Short-Term Remediation" in user_prompt

    def test_system_prompt_non_empty(self, builder: PromptBuilder, sample_cve: dict) -> None:
        system_prompt, _ = builder.build_ranking_explanation_prompt(sample_cve, {})
        assert len(system_prompt) > 50

    def test_investigation_system_prompt_mentions_evidence(self, builder: PromptBuilder, sample_scenario: dict) -> None:
        system_prompt, _ = builder.build_investigation_prompt(sample_scenario)
        assert "evidence" in system_prompt.lower() or "cite" in system_prompt.lower()


# ---------------------------------------------------------------------------
# OutputValidator tests
# ---------------------------------------------------------------------------

class TestOutputValidator:

    # --- Citation extraction ---

    def test_extract_cve_citation(self, validator: OutputValidator) -> None:
        text = "This is related to CVE-2024-12345 which has been exploited."
        cits = validator.extract_citations(text)
        assert "CVE-2024-12345" in cits

    def test_extract_technique_citation(self, validator: OutputValidator) -> None:
        text = "The attack maps to T1190 and T1059.001."
        cits = validator.extract_citations(text)
        assert "T1190" in cits

    def test_extract_score_citation(self, validator: OutputValidator) -> None:
        text = "The CVSS score is 9.8 and the risk score is 0.923."
        cits = validator.extract_citations(text)
        assert "9.8" in cits

    # --- Claim extraction ---

    def test_extract_claims_basic(self, validator: OutputValidator) -> None:
        text = "The vulnerability is critical. It should be patched immediately. No delays are acceptable."
        claims = validator.extract_claims(text)
        assert len(claims) >= 2

    def test_short_text_returns_no_claims(self, validator: OutputValidator) -> None:
        claims = validator.extract_claims("OK.")
        assert len(claims) == 0

    # --- Evidence support ---

    def test_claim_with_cve_id_always_supported(
        self, validator: OutputValidator, sample_evidence_bundle: dict
    ) -> None:
        claim = "CVE-2024-12345 is a critical vulnerability."
        result = validator.check_evidence_support(claim, sample_evidence_bundle)
        assert result is True

    def test_entirely_unrelated_claim_unsupported(
        self, validator: OutputValidator, sample_evidence_bundle: dict
    ) -> None:
        # A claim with no overlap with evidence keywords
        claim = "Elephants migrate during monsoon season annually."
        result = validator.check_evidence_support(claim, sample_evidence_bundle)
        assert result is False

    # --- Uncertainty markers ---

    def test_flag_uncertainty_markers_found(self, validator: OutputValidator) -> None:
        text = "The attacker may have gained access. This could indicate persistence."
        markers = validator.flag_uncertainty_markers(text)
        assert len(markers) >= 1

    def test_no_uncertainty_markers_in_factual_text(self, validator: OutputValidator) -> None:
        text = "CVE-2024-12345 has a CVSS score of 9.8 and is listed in the KEV catalogue."
        markers = validator.flag_uncertainty_markers(text)
        assert len(markers) == 0

    # --- Full validate ---

    def test_validate_returns_required_keys(
        self, validator: OutputValidator, sample_evidence_bundle: dict
    ) -> None:
        response = "CVE-2024-12345 is critical (CVSS 9.8) and maps to T1190."
        result = validator.validate(response, sample_evidence_bundle)
        required_keys = {
            "validated_text", "citations_found", "unsupported_claims",
            "confidence_score", "warnings",
        }
        assert required_keys.issubset(set(result.keys()))

    def test_confidence_score_in_range(
        self, validator: OutputValidator, sample_evidence_bundle: dict
    ) -> None:
        response = "CVE-2024-12345 is critical. T1190 is mapped. CVSS 9.8."
        result = validator.validate(response, sample_evidence_bundle)
        assert 0.0 <= result["confidence_score"] <= 1.0

    def test_unsupported_flag_detected_in_response(
        self, validator: OutputValidator, sample_evidence_bundle: dict
    ) -> None:
        response = "CVE-2024-12345 is critical. The attacker used zero-day exploits [UNSUPPORTED]."
        result = validator.validate(response, sample_evidence_bundle)
        assert any("self-flagged" in w.lower() for w in result["warnings"])
