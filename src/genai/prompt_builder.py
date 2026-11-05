"""
src/genai/prompt_builder.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Constructs carefully structured prompts for the LLM to reason over
vulnerability evidence bundles.

All prompts follow three principles:
1. **Evidence-grounded**: the LLM is explicitly instructed to cite specific
   evidence items and to flag any claims it cannot support.
2. **Structured output**: prompts request numbered sections so downstream
   parsing is reliable.
3. **Uncertainty-aware**: prompts instruct the LLM to hedge when evidence
   is ambiguous or absent.
"""

from __future__ import annotations

import json
from typing import Any


class PromptBuilder:
    """Assembles (system_prompt, user_prompt) pairs for each investigation task."""

    # ------------------------------------------------------------------
    # Ranking explanation
    # ------------------------------------------------------------------

    def build_ranking_explanation_prompt(
        self,
        cve: dict[str, Any],
        score_breakdown: dict[str, Any],
    ) -> tuple[str, str]:
        """Explain why a CVE received a high contextual risk score.

        Parameters
        ----------
        cve:
            CVE metadata dict (from the merged vulnerability DataFrame row).
        score_breakdown:
            Dict containing at least: ``risk_score``, ``risk_band``,
            ``cvss_v3_score``, ``in_kev``, ``matched_asset_id``.

        Returns
        -------
        tuple[str, str]
            ``(system_prompt, user_prompt)``
        """
        system_prompt = (
            "You are a senior cybersecurity analyst specialising in vulnerability risk "
            "prioritisation. Your task is to explain risk scores to a technical audience. "
            "You MUST:\n"
            "- Base every claim on the provided evidence data only.\n"
            "- Cite specific evidence fields (e.g. 'CVSS score 9.8', 'listed in CISA KEV').\n"
            "- Flag any claim that cannot be directly supported with '[UNSUPPORTED]'.\n"
            "- Use precise, professional language. Avoid speculation."
        )

        cve_id = cve.get("cve_id", "UNKNOWN")
        cvss = cve.get("cvss_v3_score", "N/A")
        severity = cve.get("cvss_v3_severity", "N/A")
        in_kev = "Yes" if cve.get("in_kev") else "No"
        description = str(cve.get("description", "No description available."))[:800]
        affected = str(cve.get("affected_products", "Unknown"))[:400]
        risk_score_raw = score_breakdown.get("risk_score", "N/A")
        risk_score_str = (
            f"{risk_score_raw:.3f}"
            if isinstance(risk_score_raw, (int, float))
            else str(risk_score_raw)
        )
        risk_band = score_breakdown.get("risk_band", "N/A")
        asset_id = score_breakdown.get("matched_asset_id", "None")

        user_prompt = f"""You have been asked to explain the risk ranking for the following CVE.

## CVE Details
- **CVE ID**: {cve_id}
- **Description**: {description}
- **CVSS v3 Score**: {cvss} ({severity})
- **In CISA KEV (actively exploited)**: {in_kev}
- **Affected Products**: {affected}

## Contextual Risk Score Breakdown
- **Overall Risk Score**: {risk_score_str} (Band: {risk_band})
- **Matched Asset**: {asset_id}
- **Score Components**: {json.dumps(score_breakdown, indent=2, default=str)}

## Your Task
Write a 3–4 paragraph explanation covering:
1. Why this CVE received this risk band (cite CVSS, KEV status, affected products).
2. What makes the matched asset particularly (or less) vulnerable.
3. What an attacker could realistically achieve if this vulnerability were exploited.
4. Any caveats or limitations in the evidence (flag with [UNSUPPORTED] if needed).

Ground every statement in the data above. Do not introduce information not present in the evidence.
"""
        return system_prompt, user_prompt

    # ------------------------------------------------------------------
    # Investigation
    # ------------------------------------------------------------------

    def build_investigation_prompt(
        self, scenario: dict[str, Any]
    ) -> tuple[str, str]:
        """Assemble a full threat investigation prompt from a scenario dict.

        The LLM is asked to produce a structured investigation report with
        hypothesis, evidence analysis, log queries, and defensive recommendations.

        Parameters
        ----------
        scenario:
            Dict as produced by ``ThreatCorrelator.build_investigation_scenario``.
            Must contain: ``cve_id``, ``asset``, ``matched_techniques``,
            ``relevant_logs``, ``evidence_summary``.

        Returns
        -------
        tuple[str, str]
            ``(system_prompt, user_prompt)``
        """
        system_prompt = (
            "You are an expert threat intelligence analyst conducting a structured "
            "vulnerability-to-threat investigation. You receive a scenario bundle containing "
            "CVE metadata, matched ATT&CK techniques, and log event evidence.\n\n"
            "RULES:\n"
            "1. State a clear investigative hypothesis in the first section.\n"
            "2. Reference specific log event IDs, technique IDs, and CVE fields as evidence.\n"
            "3. Distinguish signal events (is_noise=false) from background noise.\n"
            "4. Recommend 3–5 concrete log queries the analyst should run to verify the hypothesis.\n"
            "5. Recommend defensive actions grounded in the ATT&CK mitigations for the matched techniques.\n"
            "6. Mark any claim you cannot support from the evidence with [UNSUPPORTED].\n"
            "7. Rate your overall confidence in the investigation as: HIGH | MEDIUM | LOW, with justification."
        )

        cve_id = scenario.get("cve_id", "UNKNOWN")
        asset = scenario.get("asset", {})
        techniques = scenario.get("matched_techniques", [])
        logs = scenario.get("relevant_logs", [])
        evidence_summary = scenario.get("evidence_summary", "")

        # Truncate log data for prompt size management
        signal_logs = [ev for ev in logs if not ev.get("is_noise", False)][:10]
        noise_logs = [ev for ev in logs if ev.get("is_noise", False)][:3]

        technique_text = json.dumps(techniques, indent=2) if techniques else "No techniques matched."
        signal_log_text = json.dumps(signal_logs, indent=2, default=str) if signal_logs else "No signal logs."
        noise_log_text = json.dumps(noise_logs, indent=2, default=str) if noise_logs else "No noise logs."

        user_prompt = f"""## Investigation Scenario

### CVE
- **ID**: {cve_id}

### Asset Under Investigation
```json
{json.dumps(asset, indent=2)}
```

### Evidence Summary
{evidence_summary}

### Matched ATT&CK Techniques
```json
{technique_text}
```

### Signal Log Events (is_noise=false)
```json
{signal_log_text}
```

### Background Noise Events (for context)
```json
{noise_log_text}
```

---

## Required Output Structure

**Section 1 — Investigative Hypothesis**
State the most likely threat scenario based on the evidence.

**Section 2 — Evidence Analysis**
Analyse each signal log event, citing event_id and technique_id.

**Section 3 — Log Queries to Verify Hypothesis**
List 3–5 specific log queries (SIEM query language of your choice, labelled).

**Section 4 — Defensive Recommendations**
Provide 3–5 actionable recommendations, citing relevant ATT&CK mitigations.

**Section 5 — Confidence Assessment**
Rate confidence as HIGH / MEDIUM / LOW and justify with specific evidence gaps.
"""
        return system_prompt, user_prompt

    # ------------------------------------------------------------------
    # Remediation
    # ------------------------------------------------------------------

    def build_remediation_prompt(
        self, cve: dict[str, Any], asset: dict[str, Any]
    ) -> tuple[str, str]:
        """Build a remediation guidance prompt grounded in CVE and asset details.

        Parameters
        ----------
        cve:
            CVE metadata dict.
        asset:
            Asset dict from the inventory.

        Returns
        -------
        tuple[str, str]
            ``(system_prompt, user_prompt)``
        """
        system_prompt = (
            "You are a defensive security engineer providing remediation guidance. "
            "Your advice must be:\n"
            "- Specific to the CVE and asset described (cite CVE ID, software versions).\n"
            "- Actionable: include concrete commands, configuration changes, or patch references.\n"
            "- Prioritised: lead with the highest-impact, lowest-effort actions.\n"
            "- Honest: if a remediation is not possible for the given asset "
            "(e.g. legacy OS, no patch available), say so explicitly.\n"
            "Do not introduce generic advice not supported by the asset/CVE data."
        )

        cve_id = cve.get("cve_id", "UNKNOWN")
        cvss = cve.get("cvss_v3_score", "N/A")
        severity = cve.get("cvss_v3_severity", "N/A")
        description = str(cve.get("description", ""))[:600]
        vector = cve.get("cvss_v3_vector", "N/A")
        in_kev = "Yes — actively exploited in the wild" if cve.get("in_kev") else "No"
        required_action = cve.get("required_action", "")

        asset_id = asset.get("asset_id", "")
        hostname = asset.get("hostname", "")
        os_name = asset.get("os", "")
        software = ", ".join(asset.get("software", []))
        criticality = asset.get("criticality", "")
        exposure = asset.get("exposure", "")
        notes = asset.get("notes", "")

        user_prompt = f"""## Remediation Request

### Vulnerability
- **CVE ID**: {cve_id}
- **CVSS v3 Score**: {cvss} ({severity})
- **CVSS Vector**: {vector}
- **Actively Exploited (KEV)**: {in_kev}
- **Description**: {description}
{f"- **CISA Required Action**: {required_action}" if required_action else ""}

### Affected Asset
- **Asset ID**: {asset_id} ({hostname})
- **OS**: {os_name}
- **Installed Software**: {software}
- **Criticality**: {criticality}
- **Network Exposure**: {exposure}
- **Notes**: {notes}

---

## Required Output

**1. Immediate Actions (within 24 hours)**
Steps to reduce risk right now (isolate, disable, block).

**2. Short-Term Remediation (within 1–7 days)**
Patch, configuration change, or workaround with specific commands/references.

**3. Long-Term Hardening**
Architectural or process improvements to prevent recurrence.

**4. Limitations**
Any constraints specific to this asset that prevent full remediation.

**5. Verification**
How to confirm the remediation was successful.

Cite the CVE ID and specific software versions in your recommendations.
"""
        return system_prompt, user_prompt
