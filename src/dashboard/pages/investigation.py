"""
src/dashboard/pages/investigation.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Threat investigation page — CVE selector, automatic scenario building,
MITRE ATT&CK correlation, SIEM log evidence timeline, and AI investigation trigger.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.dashboard.custom_cve_form import render_custom_cve_form
from src.dashboard.data_loader import ensure_data_loaded

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def render() -> None:
    """Render the Threat Investigation page."""
    ensure_data_loaded()
    st.title("🔎 Threat Investigation & Evidence Correlation")
    st.markdown(
        "Correlate vulnerability findings with organizational asset context, "
        "MITRE ATT&CK threat techniques, and SIEM security log evidence."
    )

    # ----------------------------------------------------------------
    # Custom / Manual CVE Ingestion
    # ----------------------------------------------------------------
    render_custom_cve_form(title="➕ Ingest Custom / Unlisted CVE (Manual Entry or NIST NVD Live Fetch)")

    vuln_df: pd.DataFrame | None = st.session_state.get("vuln_df")

    if vuln_df is None or vuln_df.empty:
        st.info("No vulnerability data loaded. Checking database...")
        return

    # ----------------------------------------------------------------
    # CVE selector
    # ----------------------------------------------------------------
    if "risk_score" in vuln_df.columns:
        sorted_df = vuln_df.sort_values("risk_score", ascending=False)
        cve_options = sorted_df["cve_id"].dropna().tolist()
    else:
        cve_options = vuln_df["cve_id"].dropna().tolist()

    if not cve_options:
        st.warning("No CVE IDs found in the dataset.")
        return

    default_idx = 0
    if "selected_cve" in st.session_state and st.session_state["selected_cve"] in cve_options:
        default_idx = cve_options.index(st.session_state["selected_cve"])

    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        selected_cve = st.selectbox(
            "Select CVE to Investigate",
            cve_options,
            index=default_idx,
            help="Ranked by contextual risk score (highest risk first)",
        )
        st.session_state["selected_cve"] = selected_cve
    with col_sel2:
        st.write("")
        st.write("")
        force_rebuild = st.button("🔄 Re-build Scenario", use_container_width=True)

    if not selected_cve:
        return

    row = vuln_df[vuln_df["cve_id"] == selected_cve].iloc[0]

    # ----------------------------------------------------------------
    # Automatically ensure scenario is built and cached
    # ----------------------------------------------------------------
    scenario_key = f"scenario_{selected_cve}"
    if force_rebuild or scenario_key not in st.session_state:
        scenario = _build_scenario(selected_cve, row)
        st.session_state[scenario_key] = scenario
    else:
        scenario = st.session_state[scenario_key]

    st.divider()

    # ----------------------------------------------------------------
    # CVE & Asset Profile
    # ----------------------------------------------------------------
    col_cve, col_asset = st.columns(2)

    with col_cve:
        st.subheader("📋 Vulnerability Profile")
        c1, c2, c3 = st.columns(3)
        c1.metric("CVSS Base", f"{row.get('cvss_v3_score', 'N/A')}")
        c2.metric("Severity", str(row.get("cvss_v3_severity", "N/A")))
        c3.metric("CISA KEV", "🚨 Actively Exploited" if row.get("in_kev") else "Not Listed")

        risk_score_val = row.get("risk_score")
        risk_str = f"{risk_score_val:.3f}" if pd.notna(risk_score_val) and isinstance(risk_score_val, (int, float)) else "N/A"
        st.info(f"**Contextual Risk Score**: `{risk_str}` (Band: **{row.get('risk_band', 'N/A')}**)")

        with st.expander("Detailed Description & Products", expanded=False):
            st.write(str(row.get("description", "No description available.")))
            if row.get("affected_products"):
                st.caption(f"**Affected Products**: {row.get('affected_products')}")

    with col_asset:
        st.subheader("🖥️ Target Asset Environment")
        asset = scenario.get("asset", {})
        a1, a2 = st.columns(2)
        a1.metric("Hostname", asset.get("hostname", "Unknown"))
        a2.metric("Asset ID", asset.get("asset_id", "Unknown"))

        crit = str(asset.get("criticality", "medium")).capitalize()
        expo = str(asset.get("exposure", "internal")).replace("_", "-").capitalize()
        st.markdown(f"- **Criticality Tier**: `{crit}`")
        st.markdown(f"- **Network Exposure**: `{expo}` (IP: `{asset.get('ip', 'N/A')}`)")
        if asset.get("notes"):
            st.caption(f"**Notes**: {asset.get('notes')}")

    st.divider()

    # ----------------------------------------------------------------
    # Correlated ATT&CK techniques
    # ----------------------------------------------------------------
    st.subheader("🎯 Correlated MITRE ATT&CK Techniques")
    techniques = scenario.get("matched_techniques", [])
    if techniques:
        for tech in techniques:
            t_id = tech.get("id", "Unknown")
            t_name = tech.get("name", "Technique")
            t_tactics = tech.get("tactics", "N/A")
            t_desc = tech.get("description", "")

            with st.expander(f"**{t_id}** — {t_name} `[{t_tactics}]`", expanded=True):
                st.markdown(f"**Description**: {t_desc}")
    else:
        st.info("No specific ATT&CK technique mapping found for this software stack.")

    st.divider()

    # ----------------------------------------------------------------
    # SIEM Security Log Evidence
    # ----------------------------------------------------------------
    st.subheader("🗒️ Correlated SIEM Security Logs")
    logs = scenario.get("relevant_logs", [])

    if logs:
        log_df = pd.DataFrame(logs)
        signal = log_df[~log_df["is_noise"].astype(bool)] if "is_noise" in log_df.columns else log_df
        noise = log_df[log_df["is_noise"].astype(bool)] if "is_noise" in log_df.columns else pd.DataFrame()

        st.markdown(
            f"Found **{len(signal)}** suspicious security events matching threat signatures, "
            f"along with **{len(noise)}** background noise events."
        )

        display_cols = [c for c in ["timestamp", "event_type", "technique_id", "description", "source_ip", "raw_log"] if c in log_df.columns]
        st.dataframe(signal[display_cols], use_container_width=True, hide_index=True)

        if not noise.empty:
            with st.expander(f"Inspect Benign Background Noise ({len(noise)} events)"):
                st.dataframe(noise[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No log events found for this scenario.")

    st.divider()

    # ----------------------------------------------------------------
    # Action — Trigger AI Assistant
    # ----------------------------------------------------------------
    st.subheader("🤖 GenAI Threat Investigation")
    st.markdown(
        "Invoke the evidence-grounded AI assistant to formulate investigation hypotheses, "
        "defensive SIEM verification queries, and validated remediation actions."
    )

    if st.button("🚀 Run AI Investigation with Gemini", key="run_ai", type="primary", use_container_width=True):
        st.session_state["pending_investigation"] = scenario
        st.session_state["llm_result"] = None  # reset previous result
        try:
            st.switch_page("pages/ai_assistant.py")
        except Exception:
            st.session_state["current_page"] = "ai_assistant"
            st.rerun()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_scenario(cve_id: str, row: pd.Series) -> dict[str, Any]:
    """Build and return an investigation scenario from the CVE row, correlating ATT&CK and SIEM logs."""
    from src.correlation.correlator import ThreatCorrelator
    from src.pipeline.attack_client import ATTACKClient
    from src.logs.simulator import LogSimulator
    from src.assets.inventory import AssetInventory

    assets_file = _PROJECT_ROOT / "data" / "assets" / "asset_inventory.json"
    attack_file = _PROJECT_ROOT / "data" / "raw" / "attack_raw.json"
    logs_file = _PROJECT_ROOT / "data" / "logs" / "security_logs.jsonl"

    # 1. Determine matched asset
    matched_id = str(row.get("matched_asset_id", "")).strip()
    if not matched_id or matched_id == "None":
        prod_text = (str(row.get("affected_products", "")) + " " + str(row.get("description", ""))).lower()
        if any(k in prod_text for k in ["postgres", "sql", "database"]):
            matched_id = "SRV-DB-001"
        elif any(k in prod_text for k in ["vpn", "fortinet", "fortios", "gateway"]):
            matched_id = "SRV-VPN-001"
        elif any(k in prod_text for k in ["kerberos", "active directory", "domain", "windows server", "ldap"]):
            matched_id = "SRV-DC-001"
        elif any(k in prod_text for k in ["chrome", "acrobat", "pdf", "word", "office"]):
            matched_id = "WS-HR-001"
        else:
            matched_id = "SRV-WEB-001"

    matched_asset = {
        "asset_id": matched_id,
        "hostname": "web-proxy-01" if matched_id == "SRV-WEB-001" else ("db-primary-01" if matched_id == "SRV-DB-001" else ("vpn-gateway-01" if matched_id == "SRV-VPN-001" else "dc-primary-01")),
        "ip": "203.0.113.10" if matched_id == "SRV-WEB-001" else "10.10.1.20",
        "criticality": "critical",
        "exposure": "internet_facing" if matched_id in ["SRV-WEB-001", "SRV-VPN-001"] else "internal",
    }

    if assets_file.exists():
        try:
            inv = AssetInventory()
            inv.load(str(assets_file))
            asset_obj = inv.get_asset(matched_id)
            if asset_obj:
                matched_asset = asset_obj
        except Exception:
            pass

    # 2. Correlate with MITRE ATT&CK
    attack_df = pd.DataFrame()
    if attack_file.exists():
        try:
            with attack_file.open(encoding="utf-8") as fh:
                bundle = json.load(fh)
            ac = ATTACKClient()
            techs = ac.extract_techniques(bundle)
            attack_df = ac.techniques_to_dataframe(techs)
        except Exception:
            pass

    # 3. Retrieve or simulate SIEM logs
    existing_logs: list[dict[str, Any]] = []
    if logs_file.exists():
        try:
            with logs_file.open(encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        ev = json.loads(line)
                        if ev.get("cve_id") == cve_id:
                            existing_logs.append(ev)
        except Exception:
            pass

    correlator = ThreatCorrelator(attack_df=attack_df, log_events=existing_logs)
    affected_str = str(row.get("affected_products", "")) + " " + str(row.get("description", ""))
    matched_techniques = correlator.map_cve_to_techniques(cve_id, affected_str)

    if not existing_logs:
        sim = LogSimulator()
        primary_tech = matched_techniques[0]["id"] if matched_techniques else "T1190"
        existing_logs = sim.generate_scenario(
            technique_id=primary_tech,
            asset_id=matched_asset.get("asset_id", "SRV-WEB-001"),
            n_events=6,
            inject_noise=True,
        )

    risk_score_val = row.get("risk_score")
    risk_score_str = f"{risk_score_val:.3f}" if pd.notna(risk_score_val) and isinstance(risk_score_val, (int, float)) else "N/A"

    scenario: dict[str, Any] = {
        "cve_id": cve_id,
        "asset": matched_asset,
        "matched_techniques": matched_techniques,
        "relevant_logs": existing_logs,
        "evidence_summary": (
            f"CVE {cve_id} affects asset '{matched_asset.get('hostname', 'unknown')}'. "
            f"CVSS: {row.get('cvss_v3_score', 'N/A')} ({row.get('cvss_v3_severity', '')}). "
            f"In KEV: {'Yes' if row.get('in_kev') else 'No'}. "
            f"Risk Score: {risk_score_str}."
        ),
    }
    return scenario


render()
