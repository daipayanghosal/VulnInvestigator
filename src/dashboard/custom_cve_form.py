"""
src/dashboard/custom_cve_form.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reusable Streamlit component for entering or fetching custom CVEs.
Enables security analysts to ingest unlisted, zero-day, or proprietary CVEs,
compute contextual risk scores against enterprise assets, and immediately
correlate them with MITRE ATT&CK and SIEM logs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.pipeline.custom_cve import (
    calculate_custom_risk,
    check_cisa_kev_status,
    fetch_nvd_cve_details,
    ingest_custom_cve,
    is_valid_cve_id,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def render_custom_cve_form(title: str = "➕ Ingest Custom / Unlisted CVE (Manual or NIST NVD)") -> str | None:
    """Render an interactive form for entering or fetching a custom CVE.

    Returns
    -------
    str | None:
        The newly ingested CVE ID if successfully added, else None.
    """
    with st.expander(title, expanded=False):
        st.markdown(
            "Enter any CVE ID to fetch details live from the **NIST NVD REST API v2**, "
            "or manually specify details for custom/unlisted vulnerabilities. "
            "The system calculates its contextual risk score against your enterprise assets "
            "and immediately correlates it with MITRE ATT&CK techniques and SIEM logs."
        )

        col_id, col_fetch = st.columns([3, 1])

        # Current or cached form data
        cached_data: dict[str, Any] = st.session_state.get("custom_cve_form_state", {})

        with col_id:
            cve_input = st.text_input(
                "CVE Identifier",
                value=cached_data.get("cve_id", ""),
                placeholder="e.g. CVE-2024-3400, CVE-2023-38606",
                help="Standard CVE identifier format (CVE-YYYY-NNNNN)",
                key="manual_cve_id_input",
            ).strip().upper()

        with col_fetch:
            st.write("")
            st.write("")
            fetch_btn = st.button("🌐 Fetch NVD", use_container_width=True, help="Query NIST NVD REST API v2")

        if fetch_btn:
            if not cve_input:
                st.warning("Please enter a CVE ID first.")
            elif not is_valid_cve_id(cve_input):
                st.warning(f"'{cve_input}' does not match standard CVE format (CVE-YYYY-NNNNN).")
            else:
                with st.spinner(f"Querying NIST NVD for {cve_input}…"):
                    nvd_data = fetch_nvd_cve_details(cve_input)
                    in_kev = check_cisa_kev_status(cve_input)

                    if nvd_data:
                        nvd_data["in_kev"] = in_kev
                        st.session_state["custom_cve_form_state"] = nvd_data
                        st.success(f"✅ Successfully retrieved {cve_input} from NIST NVD!")
                        st.rerun()
                    else:
                        st.warning(
                            f"Could not automatically retrieve '{cve_input}' from NVD (may be unlisted or API rate-limited). "
                            "You can fill in the details manually below."
                        )
                        st.session_state["custom_cve_form_state"] = {
                            "cve_id": cve_input,
                            "in_kev": in_kev,
                        }
                        st.rerun()

        # Retrieve freshest form state
        data = st.session_state.get("custom_cve_form_state", {})
        default_cve = data.get("cve_id", cve_input or "CVE-2024-XXXX")
        default_cvss = float(data.get("cvss_v3_score", 7.5))
        default_sev = str(data.get("cvss_v3_severity", "HIGH")).upper()
        default_kev = bool(data.get("in_kev", False))
        default_products = str(data.get("affected_products", ""))
        default_desc = str(data.get("description", ""))

        st.markdown("##### 📝 Vulnerability & Asset Configuration")

        with st.form("custom_cve_ingest_form"):
            f_col1, f_col2, f_col3 = st.columns([1, 1, 1])

            with f_col1:
                cvss_val = st.slider(
                    "CVSS v3 Base Score",
                    min_value=0.0,
                    max_value=10.0,
                    value=min(10.0, max(0.0, default_cvss)),
                    step=0.1,
                    help="Base vulnerability severity (0.0 – 10.0)",
                )

            with f_col2:
                sev_options = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                sev_idx = sev_options.index(default_sev) if default_sev in sev_options else 1
                severity_val = st.selectbox("CVSS Severity", sev_options, index=sev_idx)

            with f_col3:
                st.write("")
                st.write("")
                kev_val = st.checkbox(
                    "🚨 In CISA KEV (Actively Exploited)",
                    value=default_kev,
                    help="Is this CVE known to be actively exploited in the wild?",
                )

            # Enterprise Asset Association
            inventory: list[dict[str, Any]] = st.session_state.get("asset_inventory", [])
            asset_choices: list[str] = []
            asset_map: dict[str, dict[str, Any]] = {}

            for asset in inventory:
                label = (
                    f"{asset['asset_id']} — {asset.get('hostname', '')} "
                    f"[{asset.get('criticality', '').capitalize()}, "
                    f"{asset.get('exposure', '').replace('_', '-').capitalize()}]"
                )
                asset_choices.append(label)
                asset_map[label] = asset

            if not asset_choices:
                # Fallback to standard enterprise assets
                fallback_assets = [
                    {"asset_id": "SRV-WEB-001", "hostname": "web-proxy-01", "criticality": "critical", "exposure": "internet_facing"},
                    {"asset_id": "SRV-VPN-001", "hostname": "vpn-gateway-01", "criticality": "critical", "exposure": "internet_facing"},
                    {"asset_id": "SRV-DB-001", "hostname": "db-primary-01", "criticality": "critical", "exposure": "internal"},
                    {"asset_id": "SRV-DC-001", "hostname": "dc-primary-01", "criticality": "critical", "exposure": "internal"},
                    {"asset_id": "WS-HR-001", "hostname": "hr-workstation-03", "criticality": "high", "exposure": "internal"},
                ]
                for a in fallback_assets:
                    lbl = f"{a['asset_id']} — {a['hostname']} [{a['criticality'].capitalize()}, {a['exposure'].capitalize()}]"
                    asset_choices.append(lbl)
                    asset_map[lbl] = a

            selected_asset_label = st.selectbox(
                "Target Enterprise Asset",
                asset_choices,
                help="Select the enterprise asset hosting the affected software stack",
            )
            chosen_asset = asset_map.get(selected_asset_label, {})

            products_val = st.text_input(
                "Affected Software / Product Stack",
                value=default_products,
                placeholder="e.g. Palo Alto PAN-OS, Apache HTTP Server, FortiOS",
                help="Software products affected by this CVE",
            )

            desc_val = st.text_area(
                "Vulnerability Description",
                value=default_desc,
                placeholder="Describe the vulnerability mechanics, vector, and impact…",
                help="Context description used for evidence correlation and GenAI prompt construction",
            )

            submit_btn = st.form_submit_button(
                "💾 Ingest & Calculate Contextual Risk",
                type="primary",
                use_container_width=True,
            )

            if submit_btn:
                target_cve = cve_input or default_cve
                if not target_cve or target_cve == "CVE-2024-XXXX":
                    st.error("Please enter a valid CVE ID before ingesting.")
                    return None

                # Calculate contextual risk
                risk_score, risk_band = calculate_custom_risk(
                    cvss_score=cvss_val,
                    in_kev=kev_val,
                    asset=chosen_asset,
                )

                record = {
                    "cve_id": target_cve,
                    "cvss_v3_score": cvss_val,
                    "cvss_v3_severity": severity_val,
                    "in_kev": kev_val,
                    "description": desc_val or f"Manually ingested CVE {target_cve}",
                    "affected_products": products_val or chosen_asset.get("hostname", ""),
                    "matched_asset_id": chosen_asset.get("asset_id", "SRV-WEB-001"),
                    "risk_score": risk_score,
                    "risk_band": risk_band,
                }

                current_df = st.session_state.get("vuln_df")
                db_path = _PROJECT_ROOT / "data" / "processed" / "vulninvestigator.db"

                updated_df, new_row = ingest_custom_cve(current_df, record, db_path=db_path)

                # Update session state
                st.session_state["vuln_df"] = updated_df
                st.session_state["selected_cve"] = target_cve
                # Invalidate cached scenario for this CVE so fresh correlation runs
                st.session_state.pop(f"scenario_{target_cve}", None)
                st.session_state.pop("custom_cve_form_state", None)

                st.success(
                    f"🎉 Successfully ingested **{target_cve}**! "
                    f"Contextual Risk Score: `{risk_score:.3f}` ({risk_band}) | "
                    f"Rank: #{new_row.get('rank_contextual')}."
                )
                st.rerun()

    return None
