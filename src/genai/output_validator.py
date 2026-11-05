"""
src/genai/output_validator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Validates LLM-generated investigation reports against the evidence bundle.

Validation checks:
1. **Citation extraction** — identifies explicit references to evidence fields
   (CVE IDs, technique IDs, log event IDs, asset IDs, score values).
2. **Claim support** — checks whether key terms in each extracted claim appear
   in the evidence bundle (simple term-overlap heuristic).
3. **Uncertainty markers** — flags hedged / speculative language that may
   indicate the model is guessing.
4. **Confidence score** — a lightweight composite score (0–1) summarising
   overall evidence grounding.

This is a *heuristic* validator; it does not perform semantic NLP.
Outputs feed into the evaluation metrics in ``src/evaluation/``.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Explicit reference patterns
_CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_TECHNIQUE_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?", re.IGNORECASE)
_SCORE_PATTERN = re.compile(r"\b\d+\.\d+\b")  # e.g. "9.8", "0.823"

# Uncertainty / hedging markers
_UNCERTAINTY_PHRASES = [
    r"\bmay\b", r"\bmight\b", r"\bcould\b", r"\bpossibly\b", r"\bperhaps\b",
    r"\bpotentially\b", r"\blikely\b", r"\bunlikely\b", r"\buncertain\b",
    r"\bspeculate\b", r"\bsuspect\b", r"\bappear(?:s)? to\b", r"\bseem(?:s)? to\b",
    r"\[unsupported\]", r"\bnot confirmed\b", r"\binsufficient evidence\b",
]
_UNCERTAINTY_PATTERN = re.compile(
    "|".join(_UNCERTAINTY_PHRASES), re.IGNORECASE
)


class OutputValidator:
    """Validates and annotates an LLM response against an evidence bundle.

    Usage
    -----
    >>> validator = OutputValidator()
    >>> result = validator.validate(llm_response, evidence_bundle)
    """

    # ------------------------------------------------------------------
    # Main validate
    # ------------------------------------------------------------------

    def validate(
        self, llm_response: str, evidence_bundle: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate *llm_response* against *evidence_bundle*.

        Parameters
        ----------
        llm_response:
            Raw text output from the LLM.
        evidence_bundle:
            Dict containing evidence fields — minimally ``cve_id``,
            ``asset``, ``matched_techniques``, ``relevant_logs``.

        Returns
        -------
        dict with keys:
            - ``validated_text`` (str): response with [UNSUPPORTED] annotations preserved
            - ``citations_found`` (list[str]): explicit IDs/scores cited
            - ``unsupported_claims`` (list[str]): sentences with no evidence support
            - ``confidence_score`` (float): 0–1 grounding estimate
            - ``warnings`` (list[str]): human-readable validation notes
        """
        warnings: list[str] = []

        # 1. Extract citations
        citations = self.extract_citations(llm_response)

        # 2. Extract claims (sentence-level)
        claims = self.extract_claims(llm_response)

        # 3. Check evidence support per claim
        supported: list[str] = []
        unsupported: list[str] = []
        for claim in claims:
            if self.check_evidence_support(claim, evidence_bundle):
                supported.append(claim)
            else:
                unsupported.append(claim)

        # 4. Uncertainty markers
        uncertainty_markers = self.flag_uncertainty_markers(llm_response)
        if uncertainty_markers:
            warnings.append(
                f"Hedged language detected in {len(uncertainty_markers)} passage(s)."
            )

        # 5. Check for [UNSUPPORTED] tags already in the response
        explicit_unsupported = re.findall(r"\[UNSUPPORTED\]", llm_response, re.IGNORECASE)
        if explicit_unsupported:
            warnings.append(
                f"Model self-flagged {len(explicit_unsupported)} unsupported claim(s) with [UNSUPPORTED]."
            )

        # 6. Confidence score
        total_claims = len(claims)
        if total_claims == 0:
            confidence = 0.5  # no claims → ambiguous
        else:
            support_ratio = len(supported) / total_claims
            citation_bonus = min(len(citations) * 0.05, 0.2)
            penalty = len(explicit_unsupported) * 0.05
            confidence = max(0.0, min(1.0, support_ratio + citation_bonus - penalty))

        if confidence < 0.5:
            warnings.append("Low evidence grounding score — review response carefully.")

        return {
            "validated_text": llm_response,
            "citations_found": citations,
            "unsupported_claims": unsupported,
            "confidence_score": round(confidence, 3),
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # Citation extraction
    # ------------------------------------------------------------------

    def extract_citations(self, text: str) -> list[str]:
        """Extract explicit evidence references from *text*.

        Looks for: CVE IDs (CVE-YYYY-NNNNN), ATT&CK technique IDs (Txxxx),
        and numeric scores.

        Parameters
        ----------
        text: LLM response text.

        Returns
        -------
        list[str]
            Deduplicated list of found citation strings.
        """
        cve_cits = _CVE_PATTERN.findall(text)
        tech_cits = _TECHNIQUE_PATTERN.findall(text)
        score_cits = _SCORE_PATTERN.findall(text)

        all_cits = list(set(cve_cits + tech_cits + score_cits))
        return all_cits

    # ------------------------------------------------------------------
    # Claim extraction
    # ------------------------------------------------------------------

    def extract_claims(self, text: str) -> list[str]:
        """Extract individual sentences from *text* as atomic claims.

        Splits on sentence-ending punctuation followed by whitespace.
        Filters out very short fragments (< 20 chars) and markdown headings.

        Parameters
        ----------
        text: LLM response text.

        Returns
        -------
        list[str]
            List of sentence strings.
        """
        # Normalise newlines
        normalised = re.sub(r"\n+", " ", text)
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", normalised)
        claims: list[str] = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Skip headings, very short fragments
            if len(sentence) < 20:
                continue
            if sentence.startswith("#"):
                continue
            claims.append(sentence)
        return claims

    # ------------------------------------------------------------------
    # Evidence support check
    # ------------------------------------------------------------------

    def check_evidence_support(
        self, claim: str, evidence_bundle: dict[str, Any]
    ) -> bool:
        """Return True if at least one meaningful term in *claim* appears in evidence.

        A simplified term-overlap heuristic:
        1. Build a flat string from the evidence bundle (cve_id, technique IDs,
           asset IDs, event types, descriptions).
        2. Tokenise the claim into words ≥ 5 characters.
        3. If any token appears in the evidence string, the claim is "supported".

        Parameters
        ----------
        claim:
            Sentence to check.
        evidence_bundle:
            Evidence dict (from ``ThreatCorrelator.build_investigation_scenario``
            or similar).

        Returns
        -------
        bool
        """
        evidence_text = _flatten_evidence(evidence_bundle).lower()
        claim_tokens = re.findall(r"\b[a-z0-9_\-]{5,}\b", claim.lower())

        # Always supported if claim references a CVE/technique ID explicitly
        if _CVE_PATTERN.search(claim) or _TECHNIQUE_PATTERN.search(claim):
            return True

        return any(tok in evidence_text for tok in claim_tokens)

    # ------------------------------------------------------------------
    # Uncertainty markers
    # ------------------------------------------------------------------

    def flag_uncertainty_markers(self, text: str) -> list[str]:
        """Return all passages containing hedged or speculative language.

        Parameters
        ----------
        text: LLM response text.

        Returns
        -------
        list[str]
            List of matched substrings (the surrounding phrase context).
        """
        matches: list[str] = []
        for m in _UNCERTAINTY_PATTERN.finditer(text):
            # Include up to 60 chars of context around the match
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            snippet = "…" + text[start:end].strip() + "…"
            matches.append(snippet)
        return matches


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _flatten_evidence(evidence_bundle: dict[str, Any]) -> str:
    """Recursively flatten the evidence bundle into a single searchable string."""
    parts: list[str] = []

    def _recurse(obj: Any) -> None:
        if isinstance(obj, dict):
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                _recurse(item)
        elif obj is not None:
            parts.append(str(obj))

    _recurse(evidence_bundle)
    return " ".join(parts)
