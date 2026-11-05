"""
src/dashboard/pages/investigation.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Threat investigation page — CVE selector, ATT&CK technique mapping,
log event timeline, and AI investigation trigger.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st


def render() -> None:
    """Render the Threat Investigation page."""
    st.title("🔎 Threat Investigation")
    st.markdown(
        "Select a CVE to view correlated ATT&CK techniques, relevant log events, "
        "and trigger an AI-generated investigation report."
    )

    vuln_df: pd.DataFrame | None = st.session_state.get("vuln_df")

    if vuln_df is None or vuln_df.empty:
        st.info("No vulnerability data loaded. Run the pipeline first.")
        return

    # ----------------------------------------------------------------
    # CVE selector
    # ----------------------------------------------------------------
    cve_options = vuln_df["cve_id"].dropna().tolist() if "cve_id" in vuln_df.columns else []
    if not cve_options:
        st.warning("No CVE IDs found in the dataset.")
        return

    # Sort by risk_score if available
    if "risk_score" in vuln_df.columns:
        sorted_df = vuln_df.sort_values("risk_score", ascending=False)
        cve_options = sorted_df["cve_id"].dropna().tolist()

    selected_cve = st.selectbox("Select CVE to Investigate", cve_options)

    if not selected_cve:
        return

    row = vuln_df[vuln_df["cve_id"] == selected_cve].iloc[0]

    st.divider()

    # ----------------------------------------------------------------
    # CVE Summary
    # ----------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CVSS v3 Score", f"{row.get('cvss_v3_score', 'N/A')}")
    col2.metric("Severity", str(row.get("cvss_v3_severity", "N/A")))
    col3.metric("In KEV", "✅ Yes" if row.get("in_kev") else "❌ No")
    col4.metric("Risk Score", f"{row.get('risk_score', 'N/A'):.3f}" if pd.notna(row.get("risk_score")) else "N/A")

    with st.expander("📋 Full CVE Description", expanded=False):
        st.write(str(row.get("description", "No description available.")))
        if row.get("affected_products"):
            st.markdown("**Affected Products (CPE)**")
            st.code(str(row.get("affected_products", "")))

    st.divider()

    # ----------------------------------------------------------------
    # ATT&CK techniques
    # ----------------------------------------------------------------
    st.subheader("🎯 Correlated ATT&CK Techniques")
    scenario: dict | None = st.session_state.get(f"scenario_{selected_cve}")

    if scenario:
        techniques = scenario.get("matched_techniques", [])
        if techniques:
            for tech in techniques:
                with st.expander(f"**{tech.get('id', '')}** — {tech.get('name', 'Unknown')}"):
                    st.markdown(f"**Tactics**: {tech.get('tactics', 'N/A')}")
                    st.write(tech.get("description", "No description.")[:600])
        else:
            st.info("No ATT&CK techniques correlated for this CVE.")
    else:
        st.info(
            "Scenario not yet built. Click **Build Investigation Scenario** below, "
            "or run the pipeline with correlation enabled."
        )

    if st.button("🔧 Build Investigation Scenario", key="build_scenario"):
        _build_scenario(selected_cve, row)

    st.divider()

    # ----------------------------------------------------------------
    # Log event timeline
    # ----------------------------------------------------------------
    st.subheader("🗒️ Relevant Log Events")
    if scenario:
        logs = scenario.get("relevant_logs", [])
        if logs:
            log_df = pd.DataFrame(logs)
            # Distinguish signal from noise
            signal = log_df[~log_df["is_noise"].astype(bool)] if "is_noise" in log_df.columns else log_df
            noise = log_df[log_df["is_noise"].astype(bool)] if "is_noise" in log_df.columns else pd.DataFrame()

            st.markdown(f"**Signal events**: {len(signal)} | **Noise events**: {len(noise)}")
            show_cols = [c for c in ["timestamp", "event_type", "technique_id", "description", "source_ip"] if c in log_df.columns]
            st.dataframe(signal[show_cols], use_container_width=True, hide_index=True)

            if not noise.empty and st.checkbox("Show noise events"):
                st.dataframe(noise[show_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No log events found for this scenario.")
    else:
        st.info("Build the investigation scenario to view log events.")

    st.divider()

    # ----------------------------------------------------------------
    # AI trigger
    # ----------------------------------------------------------------
    st.subheader("🤖 AI-Powered Investigation")
    if st.button("🚀 Run AI Investigation", key="run_ai", type="primary"):
        if scenario:
            st.session_state["pending_investigation"] = scenario
            st.session_state["current_page"] = "ai_assistant"
            st.rerun()
        else:
            st.warning("Please build the investigation scenario first.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_scenario(cve_id: str, row: pd.Series) -> None:
    """Build and cache a full investigation scenario from the CVE row, correlating ATT&CK and SIEM logs."""
    from pathlib import Path
    from src.correlation.correlator import ThreatCorrelator
    from src.pipeline.attack_client import ATTACKClient
    from src.logs.simulator import LogSimulator
    from src.assets.inventory import AssetInventory

    project_root = Path(__file__).resolve().parents[3]
    assets_file = project_root / "data" / "assets" / "asset_inventory.json"
    attack_file = project_root / "data" / "raw" / "attack_raw.json"
    logs_file = project_root / "data" / "logs" / "security_logs.jsonl"

    # 1. Load asset
    matched_id = str(row.get("matched_asset_id", ""))
    matched_asset: dict = {"asset_id": matched_id or "unknown", "hostname": "unknown", "software": []}
    if assets_file.exists():
        inv = AssetInventory()
        inv.load(str(assets_file))
        asset_obj = inv.get_asset(matched_id)
        if asset_obj:
            matched_asset = asset_obj

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

    # 3. Load or generate SIEM log events
    existing_logs: list[dict] = []
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

    # If no existing logs for this CVE, synthesize them
    if not existing_logs:
        sim = LogSimulator()
        primary_tech = matched_techniques[0]["id"] if matched_techniques else "T1190"
        existing_logs = sim.generate_scenario(
            technique_id=primary_tech,
            asset_id=matched_asset.get("asset_id", "SRV-WEB-001"),
            n_events=5,
            inject_noise=True,
        )

    risk_score_val = row.get("risk_score")
    risk_score_str = f"{risk_score_val:.3f}" if pd.notna(risk_score_val) and isinstance(risk_score_val, (int, float)) else "N/A"

    scenario: dict = {
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
    st.session_state[f"scenario_{cve_id}"] = scenario
    st.success(f"Investigation scenario built with {len(matched_techniques)} ATT&CK techniques and {len(existing_logs)} SIEM events.")
    st.rerun()
