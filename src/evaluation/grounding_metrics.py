"""
src/evaluation/grounding_metrics.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Metrics for evaluating evidence grounding in LLM-generated outputs.

These functions aggregate results from ``OutputValidator.validate()`` across
a collection of investigation responses to produce dataset-level statistics.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def evidence_citation_rate(responses: list[dict[str, Any]]) -> float:
    """Compute the proportion of responses that contain at least one citation.

    A "citation" is any CVE ID, ATT&CK technique ID, or numeric score that
    was detected by ``OutputValidator.extract_citations``.

    Parameters
    ----------
    responses:
        List of validated output dicts (from ``OutputValidator.validate``).
        Each must contain a ``citations_found`` key (list).

    Returns
    -------
    float
        Citation rate in [0.0, 1.0]; 0.0 if list is empty.

    Examples
    --------
    >>> responses = [{"citations_found": ["CVE-2024-1234"]}, {"citations_found": []}]
    >>> evidence_citation_rate(responses)
    0.5
    """
    if not responses:
        return 0.0
    cited = sum(1 for r in responses if r.get("citations_found"))
    return cited / len(responses)


def claim_support_rate(validated_outputs: list[dict[str, Any]]) -> float:
    """Compute the average proportion of claims that are evidence-supported.

    For each validated output, the support rate is::

        supported_claims / total_claims

    where ``supported_claims = total_claims - len(unsupported_claims)``.

    Parameters
    ----------
    validated_outputs:
        List of validated output dicts.  Each must contain
        ``unsupported_claims`` (list of unsupported sentences).

    Returns
    -------
    float
        Mean claim support rate across all responses.
    """
    if not validated_outputs:
        return 0.0

    rates: list[float] = []
    for out in validated_outputs:
        unsupported = out.get("unsupported_claims", [])
        # We don't store total_claims directly — approximate from confidence_score
        # and unsupported count.  If confidence_score is available, use it directly.
        confidence = out.get("confidence_score")
        if confidence is not None:
            rates.append(float(confidence))
        else:
            # Fallback: treat 0 unsupported as full support
            rates.append(0.0 if unsupported else 1.0)

    return sum(rates) / len(rates)


def hallucination_rate(validated_outputs: list[dict[str, Any]]) -> float:
    """Estimate the hallucination rate as the proportion of responses with
    at least one unsupported claim AND an [UNSUPPORTED] self-flag from the model.

    Parameters
    ----------
    validated_outputs:
        List of validated output dicts.

    Returns
    -------
    float
        Hallucination rate in [0.0, 1.0].
    """
    if not validated_outputs:
        return 0.0

    hallucinated = 0
    for out in validated_outputs:
        unsupported = out.get("unsupported_claims", [])
        warnings = out.get("warnings", [])
        # Flag as hallucination if there are unsupported claims AND the model
        # explicitly self-flagged (warning contains "self-flagged")
        has_self_flag = any("self-flagged" in w.lower() for w in warnings)
        if unsupported and has_self_flag:
            hallucinated += 1

    return hallucinated / len(validated_outputs)


def generate_evaluation_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate individual validated outputs into an evaluation summary report.

    Parameters
    ----------
    results:
        List of validated output dicts from ``OutputValidator.validate``.

    Returns
    -------
    dict
        Summary report with keys:
        ``total_responses``, ``evidence_citation_rate``,
        ``claim_support_rate``, ``hallucination_rate``,
        ``mean_confidence_score``, ``responses_with_warnings``.
    """
    if not results:
        return {
            "total_responses": 0,
            "evidence_citation_rate": 0.0,
            "claim_support_rate": 0.0,
            "hallucination_rate": 0.0,
            "mean_confidence_score": 0.0,
            "responses_with_warnings": 0,
        }

    confidences = [
        r.get("confidence_score", 0.0) for r in results if r.get("confidence_score") is not None
    ]
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    responses_with_warnings = sum(1 for r in results if r.get("warnings"))

    return {
        "total_responses": len(results),
        "evidence_citation_rate": evidence_citation_rate(results),
        "claim_support_rate": claim_support_rate(results),
        "hallucination_rate": hallucination_rate(results),
        "mean_confidence_score": round(mean_confidence, 4),
        "responses_with_warnings": responses_with_warnings,
    }
