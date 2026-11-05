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
    # ----------------------------------------------------------------
    # Automatically ensure scenario is built and cached
    # ----------------------------------------------------------------
    scenario_key = f"scenario_{selected_cve}"
    if force_rebuild or scenario_key not in st.session_state:
        scenario = _build_scenario(selected_cve, row)
        st.session_state[scenario_key] = scenario
    else:
        scenario = st.session_state[scenario_key]

    asset = scenario.get("asset", {})
    breakdown = _calculate_factor_breakdown(row, asset)

    st.divider()

    # ----------------------------------------------------------------
    # Hero Scoreboard: CVSS vs Contextual Risk Comparison
    # ----------------------------------------------------------------
    st.subheader("🎯 Risk Prioritization: Baseline CVSS vs. Contextual Risk")

    col_hero_cvss, col_hero_ctx, col_hero_kev, col_hero_shift = st.columns([1.1, 1.4, 1.2, 1.2])

    with col_hero_cvss:
        st.metric(
            label="🌐 Standard CVSS Base",
            value=f"{row.get('cvss_v3_score', 'N/A')} / 10",
            delta=f"Severity: {row.get('cvss_v3_severity', 'N/A')}",
            delta_color="off",
            help="Theoretical technical severity from NVD without organizational context",
        )

    with col_hero_ctx:
        risk_score_val = row.get("risk_score")
        risk_str = f"{risk_score_val:.3f}" if pd.notna(risk_score_val) and isinstance(risk_score_val, (int, float)) else "N/A"
        band_val = str(row.get("risk_band", "High"))
        st.metric(
            label="🎯 Contextual Risk Score",
            value=f"{risk_str} / 1.0",
            delta=f"Band: {band_val.upper()}",
            delta_color="normal" if band_val in ["Critical", "High"] else "inverse",
            help="Weighted score combining CVSS (35%) + CISA KEV (30%) + Asset Criticality (20%) + Network Exposure (15%)",
        )

    with col_hero_kev:
        in_kev = bool(row.get("in_kev", False))
        st.metric(
            label="🚨 CISA KEV Exploit Status",
            value="Actively Exploited" if in_kev else "Not In KEV",
            delta="Threat Actor Weaponized" if in_kev else "No Wild Exploits Known",
            delta_color="inverse" if in_kev else "off",
            help="Whether CISA has confirmed real-world weaponization in the wild",
        )

    with col_hero_shift:
        disp = row.get("rank_displacement")
        if pd.notna(disp) and isinstance(disp, (int, float)):
            disp_int = int(disp)
            disp_sign = "+" if disp_int > 0 else ""
            delta_label = "Escalated in Queue" if disp_int > 0 else ("De-escalated in Queue" if disp_int < 0 else "Unchanged")
            st.metric(
                label="📐 Priority Rank Shift",
                value=f"{disp_sign}{disp_int} spots",
                delta=f"Rank #{row.get('rank_contextual', 'N/A')} (CVSS #{row.get('rank_cvss', 'N/A')})",
                delta_color="normal" if disp_int > 0 else "inverse",
                help="Shift in remediation queue priority compared to generic CVSS rank",
            )
        else:
            st.metric("📐 Contextual Rank", f"#{row.get('rank_contextual', 'N/A')}")

    # ----------------------------------------------------------------
    # Executive Justification Box (For Non-Technical Evaluators)
    # ----------------------------------------------------------------
    _render_justification_box(row, asset, breakdown)

    st.divider()

    # ----------------------------------------------------------------
    # CVE & Asset Profile Details
    # ----------------------------------------------------------------
    col_cve, col_asset = st.columns(2)

    with col_cve:
        st.subheader("📋 Vulnerability Details & Mechanics")
        st.markdown(f"**CVE ID**: `{selected_cve}`")
        if row.get("cvss_v3_vector"):
            st.caption(f"**CVSS Vector**: `{row.get('cvss_v3_vector')}`")

        with st.expander("Detailed Description & Products", expanded=True):
            st.write(str(row.get("description", "No description available.")))
            if row.get("affected_products"):
                st.markdown(f"**Affected Software**: `{row.get('affected_products')}`")

    with col_asset:
        st.subheader("🖥️ Target Asset Environment")
        a1, a2 = st.columns(2)
        a1.metric("Hostname", asset.get("hostname", "Unknown"))
        a2.metric("Asset ID", asset.get("asset_id", "Unknown"))

        crit = str(asset.get("criticality", "medium")).capitalize()
        expo = str(asset.get("exposure", "internal")).replace("_", "-").capitalize()
        st.markdown(f"- **Criticality Tier**: `{crit}`")
        st.markdown(f"- **Network Exposure**: `{expo}` (IP: `{asset.get('ip', 'N/A')}`)")
        if asset.get("notes"):
            st.caption(f"**Role**: {asset.get('notes')}")
        if asset.get("software"):
            sw_list = asset.get("software")
            if isinstance(sw_list, list):
                st.caption(f"**Installed Stack**: {', '.join(sw_list)}")

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


def _calculate_factor_breakdown(row: pd.Series, asset: dict[str, Any]) -> dict[str, Any]:
    """Calculate the 4-factor mathematical breakdown of the contextual risk score."""
    raw_cvss = row.get("cvss_v3_score", 0.0)
    cvss_val = float(raw_cvss) if pd.notna(raw_cvss) and isinstance(raw_cvss, (int, float)) else 0.0
    cvss_norm = cvss_val / 10.0
    cvss_contrib = 0.35 * cvss_norm

    in_kev = bool(row.get("in_kev", False))
    kev_contrib = 0.30 if in_kev else 0.0

    crit_tier = str(asset.get("criticality", "medium")).lower()
    crit_map = {"critical": 1.0, "high": 0.75, "medium": 0.50, "low": 0.25, "unknown": 0.10}
    crit_score = crit_map.get(crit_tier, 0.50)
    asset_contrib = 0.20 * crit_score

    expo_tier = str(asset.get("exposure", "internal")).lower()
    expo_map = {
        "internet_facing": 1.0,
        "dmz": 0.75,
        "internal": 0.50,
        "restricted": 0.25,
        "air_gapped": 0.0,
    }
    expo_score = expo_map.get(expo_tier, 0.50)
    expo_contrib = 0.15 * expo_score

    total_score = cvss_contrib + kev_contrib + asset_contrib + expo_contrib

    return {
        "cvss_val": cvss_val,
        "cvss_norm": cvss_norm,
        "cvss_contrib": cvss_contrib,
        "in_kev": in_kev,
        "kev_contrib": kev_contrib,
        "crit_tier": crit_tier,
        "crit_score": crit_score,
        "asset_contrib": asset_contrib,
        "expo_tier": expo_tier,
        "expo_score": expo_score,
        "expo_contrib": expo_contrib,
        "total_score": total_score,
    }


def _render_justification_box(row: pd.Series, asset: dict[str, Any], breakdown: dict[str, Any]) -> None:
    """Render plain-English executive justification and factor breakdown for evaluators."""
    cvss_val = breakdown["cvss_val"]
    total_score = breakdown["total_score"]
    in_kev = breakdown["in_kev"]
    crit_tier = breakdown["crit_tier"].capitalize()
    expo_tier = breakdown["expo_tier"].replace("_", "-").capitalize()
    hostname = asset.get("hostname", "the target server")
    asset_id = asset.get("asset_id", "Unknown")
    band = str(row.get("risk_band", "High"))

    disp = row.get("rank_displacement", 0)
    disp_int = int(disp) if pd.notna(disp) and isinstance(disp, (int, float)) else 0

    with st.container(border=True):
        st.markdown("### 💡 Executive Justification: Why Contextual Risk Differs from CVSS")
        st.caption("*(Plain-English explanation designed for non-technical evaluators, examiners, and leadership)*")

        # Non-Technical Analogy Card
        st.info(
            "🎯 **Analogy for Non-Technical Evaluators**:\n\n"
            f"• **Standard CVSS ({cvss_val:.1f} / 10)** is like a laboratory fire-hazard rating on a boiler: it measures how violently "
            "it could burst under theoretical test conditions in a lab.\n\n"
            f"• **Our Contextual Risk Score ({total_score:.3f} / 1.0)** checks reality: is the boiler **actually leaking right now** (CISA KEV), "
            f"is it placed inside your **most critical server room** (`{hostname}` - Criticality: {crit_tier}), "
            f"and are the **doors wide open to the public street** (Exposure: {expo_tier})?"
        )

        # Plain-English Executive Verdict
        if in_kev and "internet" in expo_tier.lower():
            verdict_text = (
                f"🚨 **Threat Escalation Justification**: While generic CVSS rates this flaw at a moderate **{cvss_val:.1f}**, "
                f"standard scoring dangerously ignores active adversary campaigns. This CVE is **actively weaponized in the wild** "
                f"(verified in CISA's KEV catalogue) and directly affects an **Internet-facing, {crit_tier} asset** (`{hostname}`). "
                f"Our engine elevates its risk score to **{total_score:.3f} ({band})**, "
                f"surging its priority queue rank by **{abs(disp_int)} positions** to prevent an imminent enterprise intrusion."
            )
        elif not in_kev:
            verdict_text = (
                f"🛡️ **De-escalation & Alert-Fatigue Prevention**: Generic CVSS assigns a severe score of **{cvss_val:.1f}**, "
                f"treating this vulnerability as an emergency in a vacuum. However, in your enterprise perimeter, "
                f"**CISA has found zero evidence of active wild exploitation (0.00 KEV contribution)**. "
                f"Even though `{hostname}` is a **{crit_tier}** system, the absence of weaponized exploit kits "
                f"reduces true operational urgency to **{total_score:.3f} ({band})**, moving it **{abs(disp_int)} spots down the priority queue**. "
                f"This prevents engineering teams from wasting hours on panic patching for unexploited bugs."
            )
        else:
            verdict_text = (
                f"⚖️ **Balanced Prioritization Justification**: Standard CVSS evaluates technical severity in isolation (**{cvss_val:.1f}**). "
                f"Factoring in its CISA KEV exploitation state, the **{crit_tier}** operational role of `{hostname}`, "
                f"and its **{expo_tier}** network perimeter, our engine calculates a calibrated risk score of **{total_score:.3f} ({band})**."
            )

        st.markdown(verdict_text)
        st.divider()

        # The 4-Factor Mathematical Transparency Grid
        st.markdown("**📊 Mathematical Factor Contribution Breakdown (Weights Sum to 100%)**")

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.metric(
                label="1. CVSS Flaw Base (35%)",
                value=f"+{breakdown['cvss_contrib']:.3f}",
                delta=f"CVSS: {cvss_val:.1f} / 10",
                delta_color="off",
                help="Baseline technical severity (CVSS / 10 × 0.35)",
            )
            st.caption("Theoretical flaw severity in isolation")

        with f2:
            st.metric(
                label="2. Real Exploits / KEV (30%)",
                value=f"+{breakdown['kev_contrib']:.3f}",
                delta="🚨 In KEV (+0.300)" if in_kev else "🛡️ Not Exploited (+0.000)",
                delta_color="normal" if in_kev else "off",
                help="Active threat actor weaponization verified by CISA KEV (1.0 × 0.30 if in KEV, else 0.0)",
            )
            st.caption("Observed in real-world attacks")

        with f3:
            st.metric(
                label="3. Asset Criticality (20%)",
                value=f"+{breakdown['asset_contrib']:.3f}",
                delta=f"Tier: {crit_tier}",
                delta_color="off",
                help=f"Asset operational importance score ({breakdown['crit_score']:.2f} × 0.20)",
            )
            st.caption(f"Business impact on `{hostname}`")

        with f4:
            st.metric(
                label="4. Network Exposure (15%)",
                value=f"+{breakdown['expo_contrib']:.3f}",
                delta=f"Tier: {expo_tier}",
                delta_color="off",
                help=f"Perimeter exposure score ({breakdown['expo_score']:.2f} × 0.15)",
            )
            st.caption("Perimeter attack surface access")

        st.markdown(
            f"""
            $$\\text{{Contextual Risk Score}} = \\underbrace{{{breakdown['cvss_contrib']:.3f}}}_\\text{{CVSS (35\\%)}} + \\underbrace{{{breakdown['kev_contrib']:.3f}}}_\\text{{CISA KEV (30\\%)}} + \\underbrace{{{breakdown['asset_contrib']:.3f}}}_\\text{{Asset (20\\%)}} + \\underbrace{{{breakdown['expo_contrib']:.3f}}}_\\text{{Exposure (15\\%)}} = \\mathbf{{{total_score:.3f}}}$$
            """
        )


render()
