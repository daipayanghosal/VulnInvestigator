"""
src/dashboard/pages/ai_assistant.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
AI Assistant page — displays LLM investigation reports with citation badges
and evidence-grounding scores.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import streamlit as st

from src.dashboard.data_loader import ensure_data_loaded

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def render() -> None:
    """Render the AI Assistant page."""
    ensure_data_loaded()

    with st.sidebar:
        st.subheader("🔑 Gemini API Status")
        has_key = bool(
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or (hasattr(st, "secrets") and ("GEMINI_API_KEY" in st.secrets or "GOOGLE_API_KEY" in st.secrets))
            or st.session_state.get("gemini_api_key")
        )
        if has_key:
            st.success("✅ Gemini API Key Active")
        else:
            st.warning("⚠️ No Gemini API Key Configured")
            st.caption(
                "Add `GEMINI_API_KEY` to **Streamlit Cloud Secrets** or paste it below to enable live queries."
            )

        custom_key = st.text_input(
            "Gemini API Key Override",
            type="password",
            value=st.session_state.get("gemini_api_key", ""),
            help="If not configured in Streamlit Cloud Secrets, paste your key here.",
        )
        if custom_key:
            st.session_state["gemini_api_key"] = custom_key.strip()
            os.environ["GEMINI_API_KEY"] = custom_key.strip()

    st.title("🤖 AI Assistant — Evidence-Grounded Threat Investigation")
    st.markdown(
        "AI-generated investigation report grounded in vulnerability evidence.  "
        "Citations are highlighted; unsupported claims are flagged in yellow."
    )

    # ----------------------------------------------------------------
    # Non-Technical & Executive Guide
    # ----------------------------------------------------------------
    with st.expander("💡 Executive & Non-Technical Guide: What is Evidence-Grounded GenAI?", expanded=False):
        st.markdown(
            """
### 🧠 Plain-English Guide to Evidence-Grounded AI

**Why Generic AI Can Be Dangerous in Cybersecurity**:  
Standard large language models (like basic chatbots) have a well-known flaw: **hallucination**. They frequently generate confident, convincing explanations that are completely fabricated. In cyber defense, acting on a hallucinated IP address or made-up attack vector wastes hundreds of hours and leaves systems exposed.

**How VulnInvestigator Solves This**:  
This system implements **Evidence-Grounded Generative AI** using Google Gemini combined with automated deterministic output verification:

1. **Strict Evidence Ingestion**: The AI is fed only concrete facts: the specific CVE record, affected software stack, verified asset attributes, and raw SIEM log events.
2. **Automated Citation Badging (Blue Badges)**: The validator scans every sentence to ensure the AI explicitly cites tangible evidence tokens (such as `CVE-2024-XXXX`, `T1190`, or specific log event IDs).
3. **Automated Hallucination Detection (Yellow Highlight)**: Any sentence that contains speculative claims or ungrounded assertions is highlighted in <mark style="background:#fff3cd;padding:2px 4px;border-radius:3px;">yellow</mark>, alerting human analysts to verify the claim before taking action.

---
### 📊 Understanding the Quality Metrics:
* **Evidence Grounding Score**: A composite confidence score (0%–100%) measuring how strictly the report is supported by verifiable log and threat evidence.
* **Citations Found**: The count of verifiable evidence items quoted by the AI.
* **Unsupported Claims**: The count of unverified assertions flagged for human review.
            """
        )

    # ----------------------------------------------------------------
    # Check for pending investigation scenario
    # ----------------------------------------------------------------
    scenario: dict | None = st.session_state.get("pending_investigation")
    llm_result: dict | None = st.session_state.get("llm_result")

    if scenario is None and llm_result is None:
        st.info(
            "No active investigation.  "
            "Go to **Threat Investigation**, select a CVE, build a scenario, "
            "and click **Run AI Investigation**."
        )
        _render_demo_report()
        return

    # ----------------------------------------------------------------
    # Run LLM if scenario is pending
    # ----------------------------------------------------------------
    if scenario and not llm_result:
        with st.spinner("🤖 Running AI investigation — this may take 10–30 seconds…"):
            llm_result = _run_investigation(scenario)
            st.session_state["llm_result"] = llm_result
            st.session_state["pending_investigation"] = None

    if llm_result is None:
        st.error("Investigation failed. Check LLM configuration and retry.")
        return

    # ----------------------------------------------------------------
    # Display results
    # ----------------------------------------------------------------
    cve_id = llm_result.get("cve_id", "Unknown CVE")
    st.subheader(f"Investigation Report — {cve_id}")

    # Evidence grounding score
    confidence = llm_result.get("confidence_score", 0.0)
    citations = llm_result.get("citations_found", [])
    unsupported = llm_result.get("unsupported_claims", [])
    warnings = llm_result.get("warnings", [])

    col1, col2, col3 = st.columns(3)
    col1.metric("Evidence Grounding Score", f"{confidence:.1%}", help="0–100%: how well-supported the report is")
    col2.metric("Citations Found", len(citations))
    col3.metric("Unsupported Claims", len(unsupported))

    # Warnings
    if warnings:
        for w in warnings:
            st.warning(f"⚠️ {w}")

    st.divider()

    # Citation badges
    if citations:
        st.markdown("**📌 Evidence Citations Detected**")
        badge_html = " ".join(
            f'<span style="background:#1f77b4;color:white;padding:2px 6px;'
            f'border-radius:4px;margin:2px;font-size:0.8em;">{c}</span>'
            for c in citations
        )
        st.markdown(badge_html, unsafe_allow_html=True)
        st.divider()

    # Main report text
    st.subheader("📄 Investigation Report")
    report_text = llm_result.get("validated_text", "No report generated.")

    # Highlight unsupported claims in yellow
    highlighted = _highlight_unsupported(report_text, unsupported)
    st.markdown(highlighted, unsafe_allow_html=True)

    st.divider()

    # Unsupported claims detail
    if unsupported:
        with st.expander(f"⚠️ {len(unsupported)} Potentially Unsupported Claim(s)", expanded=False):
            st.markdown(
                "_These sentences could not be directly linked to evidence in the bundle. "
                "Review them carefully._"
            )
            for i, claim in enumerate(unsupported[:10], 1):
                st.markdown(
                    f'<div style="background:#fff3cd;padding:8px;border-radius:4px;margin:4px 0;">'
                    f"{i}. {claim}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Clear button
    if st.button("🗑️ Clear Report"):
        st.session_state.pop("llm_result", None)
        st.rerun()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _run_investigation(scenario: dict) -> dict | None:
    """Run the LLM investigation and validate output."""
    try:
        import yaml
        from src.genai.llm_client import get_llm_client
        from src.genai.prompt_builder import PromptBuilder
        from src.genai.output_validator import OutputValidator

        config_path = _PROJECT_ROOT / "config" / "settings.yaml"
        with config_path.open() as fh:
            cfg = yaml.safe_load(fh)
        llm_cfg = cfg.get("llm", {})

        client = get_llm_client(
            backend=llm_cfg.get("backend", "gemini"),
            model=llm_cfg.get("model", "gemini-3.5-flash"),
            temperature=llm_cfg.get("temperature", 0.2),
            max_tokens=llm_cfg.get("max_tokens", 2048),
        )

        builder = PromptBuilder()
        system_p, user_p = builder.build_investigation_prompt(scenario)
        response = client.complete(system_p, user_p)

        validator = OutputValidator()
        result = validator.validate(response, scenario)
        result["cve_id"] = scenario.get("cve_id", "Unknown")
        return result

    except Exception as exc:  # noqa: BLE001
        err_msg = str(exc)
        if "API key" in err_msg or "GEMINI_API_KEY" in err_msg or "api_key" in err_msg:
            st.error(
                "🔑 **Gemini API Key Required**\n\n"
                "To enable live Gemini investigations on Streamlit Community Cloud:\n"
                "1. Click **Manage app** (bottom-right) or `⋮` ➔ **Settings** ➔ **Secrets**.\n"
                "2. Add:\n"
                "   ```toml\n"
                "   GEMINI_API_KEY = \"your-gemini-api-key\"\n"
                "   ```\n"
                "3. Click **Save**.\n\n"
                "_You can also enter your key temporarily in the left sidebar under 'Gemini API Key Override'._"
            )
        else:
            st.error(f"LLM error: {exc}")
        return None


def _highlight_unsupported(text: str, unsupported: list[str]) -> str:
    """Wrap unsupported claim sentences in yellow highlight HTML."""
    for claim in unsupported:
        escaped = re.escape(claim[:60])  # match on first 60 chars to avoid regex issues
        text = re.sub(
            escaped,
            f'<mark style="background:#fff3cd;">{claim[:60]}</mark>',
            text,
            count=1,
        )
    return text


def _render_demo_report() -> None:
    """Display a static demo report when no investigation has been run."""
    st.markdown("---")
    st.subheader("📄 Demo Report (Placeholder)")
    st.markdown(
        """
> **Note**: This is a placeholder report to illustrate the output format.

**Section 1 — Investigative Hypothesis**
Based on the evidence, the most likely scenario is an adversary exploiting
**CVE-2024-XXXX** (CVSS 9.8) against the public-facing web proxy `SRV-WEB-001`.
The exploit aligns with **T1190** (Exploit Public-Facing Application).

**Section 2 — Evidence Analysis**
- Event `abc-123`: POST request with path traversal payload → corroborates T1190.
- Event `def-456`: Web shell written to `/var/www/html/shell.php` → indicates
  successful exploitation.

**Section 3 — Log Queries**
1. `index=web_logs sourcetype=apache method=POST uri="*.php" status=200`
2. `index=endpoint source="/var/www/html/*.php" action=CREATE`

**Section 4 — Defensive Recommendations**
1. Apply vendor patch immediately (CVE CVSS 9.8, in CISA KEV).
2. Enable WAF rule blocking path traversal patterns.
3. Rotate all credentials accessible from `SRV-WEB-001`.

**Section 5 — Confidence Assessment**: **MEDIUM** — two corroborating log events
found; full filesystem audit required to confirm web shell persistence.
"""
    )


render()
