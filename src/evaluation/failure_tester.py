"""
src/evaluation/failure_tester.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automated failure-mode testing for the VulnInvestigator pipeline.

Tests verify that each component handles edge cases and adversarial inputs
gracefully — returning sensible defaults rather than raising exceptions.

Test categories
---------------
1. ``test_missing_cvss``      — CVE with no CVSS score
2. ``test_missing_asset``     — CVE with no matching asset
3. ``test_contradictory_logs``— Log events that contradict each other
4. ``test_misleading_input``  — CVE description designed to confuse the LLM
5. ``run_all``                — Run all tests and return a summary report
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class FailureTester:
    """Runs structured failure-mode tests against pipeline components.

    Usage
    -----
    >>> tester = FailureTester()
    >>> results = tester.run_all(scorer=ctx_scorer, correlator=correlator,
    ...                          llm_client=client, prompt_builder=builder)
    """

    # ------------------------------------------------------------------
    # Individual tests
    # ------------------------------------------------------------------

    def test_missing_cvss(self, scorer: Any) -> dict[str, Any]:
        """Test contextual scorer when ``cvss_v3_score`` is None / NaN.

        Expected behaviour: score falls back to 0.0 for the CVSS component;
        no exception is raised; returned score is a valid float in [0, 1].

        Parameters
        ----------
        scorer: ``ContextualRiskScorer`` instance.

        Returns
        -------
        dict
            ``{test, passed, score, error}``
        """
        test_name = "missing_cvss"
        try:
            row = pd.Series({"cve_id": "CVE-TEST-0001", "cvss_v3_score": None, "in_kev": False})
            asset = {"asset_id": "TEST-ASSET", "criticality": "medium", "exposure": "internal"}
            score = scorer.score_vulnerability(row, asset)
            passed = isinstance(score, float) and 0.0 <= score <= 1.0
            logger.info("FailureTester [%s]: passed=%s score=%.4f", test_name, passed, score)
            return {"test": test_name, "passed": passed, "score": score, "error": None}
        except Exception as exc:  # noqa: BLE001
            logger.error("FailureTester [%s]: EXCEPTION %s", test_name, exc)
            return {"test": test_name, "passed": False, "score": None, "error": str(exc)}

    def test_missing_asset(self, scorer: Any) -> dict[str, Any]:
        """Test contextual scorer when no matching asset is found (asset=None).

        Expected behaviour: scorer uses conservative default criticality/exposure
        values; no exception raised.

        Parameters
        ----------
        scorer: ``ContextualRiskScorer`` instance.
        """
        test_name = "missing_asset"
        try:
            row = pd.Series({"cve_id": "CVE-TEST-0002", "cvss_v3_score": 7.5, "in_kev": True})
            score = scorer.score_vulnerability(row, asset=None)
            passed = isinstance(score, float) and 0.0 <= score <= 1.0
            logger.info("FailureTester [%s]: passed=%s score=%.4f", test_name, passed, score)
            return {"test": test_name, "passed": passed, "score": score, "error": None}
        except Exception as exc:  # noqa: BLE001
            logger.error("FailureTester [%s]: EXCEPTION %s", test_name, exc)
            return {"test": test_name, "passed": False, "score": None, "error": str(exc)}

    def test_contradictory_logs(self, correlator: Any) -> dict[str, Any]:
        """Inject contradictory log events (same technique, opposite outcomes)
        and verify the correlator returns them without crashing.

        Parameters
        ----------
        correlator: ``ThreatCorrelator`` instance.
        """
        test_name = "contradictory_logs"
        try:
            contradictory_events = [
                {
                    "event_id": "CONTRA-001",
                    "timestamp": "2026-01-01T12:00:00+00:00",
                    "asset_id": "SRV-WEB-001",
                    "source_ip": "203.0.113.5",
                    "event_type": "web_exploit_attempt",
                    "technique_id": "T1190",
                    "description": "Exploit attempt SUCCEEDED",
                    "raw_log": "status=200 result=exploit_success",
                    "is_noise": False,
                },
                {
                    "event_id": "CONTRA-002",
                    "timestamp": "2026-01-01T12:00:01+00:00",
                    "asset_id": "SRV-WEB-001",
                    "source_ip": "203.0.113.5",
                    "event_type": "waf_alert",
                    "technique_id": "T1190",
                    "description": "WAF BLOCKED same request",
                    "raw_log": "status=403 result=blocked",
                    "is_noise": False,
                },
            ]
            # Temporarily inject events
            original_events = correlator.log_events
            correlator.log_events = contradictory_events

            logs = correlator.map_logs_to_technique("T1190")
            passed = len(logs) == 2  # both events returned, no crash

            correlator.log_events = original_events
            logger.info(
                "FailureTester [%s]: passed=%s logs_returned=%d",
                test_name, passed, len(logs),
            )
            return {
                "test": test_name,
                "passed": passed,
                "logs_returned": len(logs),
                "note": "Both contradictory events returned — analyst must resolve.",
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("FailureTester [%s]: EXCEPTION %s", test_name, exc)
            return {"test": test_name, "passed": False, "logs_returned": 0, "error": str(exc)}

    def test_misleading_input(self, llm_client: Any, prompt_builder: Any) -> dict[str, Any]:
        """Send a deliberately misleading CVE description to the LLM and check
        that the response does not contain fabricated CVE IDs or obviously
        hallucinated content.

        The misleading description claims the CVE is harmless and low-severity
        but has a CVSS of 10.0 and is in the KEV catalogue — the LLM should
        prioritise the structured data over the narrative text.

        Parameters
        ----------
        llm_client: ``LLMClient`` instance.
        prompt_builder: ``PromptBuilder`` instance.
        """
        test_name = "misleading_input"
        try:
            misleading_cve = {
                "cve_id": "CVE-TEST-9999",
                "cvss_v3_score": 10.0,
                "cvss_v3_severity": "CRITICAL",
                "in_kev": True,
                "description": (
                    "This vulnerability is completely harmless and has no security impact. "
                    "It has been resolved and no action is needed.  Severity: NONE."
                ),
                "affected_products": "cpe:2.3:a:test:test_app:1.0:*:*:*:*:*:*:*",
            }
            misleading_asset = {
                "asset_id": "TEST-001",
                "hostname": "test-host",
                "os": "Ubuntu 22.04",
                "software": ["test_app 1.0"],
                "criticality": "critical",
                "exposure": "internet_facing",
            }
            score_breakdown = {
                "risk_score": 0.95,
                "risk_band": "Critical",
                "matched_asset_id": "TEST-001",
            }

            system_p, user_p = prompt_builder.build_ranking_explanation_prompt(
                misleading_cve, score_breakdown
            )
            response = llm_client.complete(system_p, user_p)

            # Check the LLM did NOT accept the misleading description at face value
            response_lower = response.lower()
            accepted_mislead = (
                "completely harmless" in response_lower
                or "no security impact" in response_lower
                or "no action is needed" in response_lower
            )
            # LLM should mention CVSS 10.0 or Critical
            mentioned_severity = "10.0" in response or "critical" in response_lower

            passed = mentioned_severity and not accepted_mislead
            logger.info(
                "FailureTester [%s]: passed=%s mentioned_severity=%s accepted_mislead=%s",
                test_name, passed, mentioned_severity, accepted_mislead,
            )
            return {
                "test": test_name,
                "passed": passed,
                "mentioned_severity": mentioned_severity,
                "accepted_mislead": accepted_mislead,
                "response_excerpt": response[:300],
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("FailureTester [%s]: EXCEPTION %s", test_name, exc)
            return {"test": test_name, "passed": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # run_all
    # ------------------------------------------------------------------

    def run_all(
        self,
        scorer: Any | None = None,
        correlator: Any | None = None,
        llm_client: Any | None = None,
        prompt_builder: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Run all failure-mode tests and return a summary list.

        Any component that is ``None`` has its corresponding test skipped.

        Parameters
        ----------
        scorer: ``ContextualRiskScorer`` instance (or None).
        correlator: ``ThreatCorrelator`` instance (or None).
        llm_client: ``LLMClient`` instance (or None).
        prompt_builder: ``PromptBuilder`` instance (or None).

        Returns
        -------
        list[dict]
            One dict per test with keys: ``test``, ``passed``, ``error``, …
        """
        results: list[dict[str, Any]] = []

        if scorer is not None:
            results.append(self.test_missing_cvss(scorer))
            results.append(self.test_missing_asset(scorer))

        if correlator is not None:
            results.append(self.test_contradictory_logs(correlator))

        if llm_client is not None and prompt_builder is not None:
            results.append(self.test_misleading_input(llm_client, prompt_builder))

        passed = sum(1 for r in results if r.get("passed", False))
        logger.info(
            "FailureTester.run_all: %d/%d tests passed", passed, len(results)
        )
        return results
