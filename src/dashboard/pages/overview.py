"""
src/dashboard/pages/overview.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Overview page — high-level metrics and top-CVE bar chart.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render() -> None:
    """Render the Overview dashboard page."""
    st.title("🏠 Overview")
    st.markdown(
        "High-level snapshot of the vulnerability dataset and contextual risk landscape."
    )

    # ----------------------------------------------------------------
    # Load data from session state (populated by pipeline)
    # ----------------------------------------------------------------
    vuln_df: pd.DataFrame | None = st.session_state.get("vuln_df")

    if vuln_df is None or vuln_df.empty:
        st.info(
            "No vulnerability data loaded yet.  "
            "Run `scripts/run_pipeline.py` to fetch and process data, "
            "then reload this page."
        )
        _render_placeholder_chart()
        return

    # ----------------------------------------------------------------
    # Metric cards
    # ----------------------------------------------------------------
    total_cves = len(vuln_df)
    in_kev = int(vuln_df["in_kev"].sum()) if "in_kev" in vuln_df.columns else 0
    critical_risk = int(
        (vuln_df["risk_band"] == "Critical").sum()
    ) if "risk_band" in vuln_df.columns else 0
    has_cvss = int(vuln_df["cvss_v3_score"].notna().sum()) if "cvss_v3_score" in vuln_df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total CVEs", f"{total_cves:,}")
    col2.metric("In CISA KEV", f"{in_kev:,}", help="Actively exploited in the wild")
    col3.metric("Critical Risk Band", f"{critical_risk:,}")
    col4.metric("Have CVSS v3 Score", f"{has_cvss:,}")

    st.divider()

    # ----------------------------------------------------------------
    # Top 5 by risk score
    # ----------------------------------------------------------------
    st.subheader("🔺 Top 5 CVEs by Contextual Risk Score")
    if "risk_score" in vuln_df.columns:
        top5_cols = ["cve_id", "cvss_v3_score", "cvss_v3_severity", "in_kev", "risk_score", "risk_band"]
        top5_cols = [c for c in top5_cols if c in vuln_df.columns]
        top5 = vuln_df.sort_values("risk_score", ascending=False).head(5)[top5_cols]
        st.dataframe(top5, use_container_width=True)
    else:
        st.warning("Contextual risk scores not yet computed. Run the pipeline first.")

    st.divider()

    # ----------------------------------------------------------------
    # Top 10 bar chart
    # ----------------------------------------------------------------
    st.subheader("📊 Top 10 CVEs by Contextual Risk Score")
    if "risk_score" in vuln_df.columns and "cve_id" in vuln_df.columns:
        top10 = vuln_df.sort_values("risk_score", ascending=False).head(10)
        color_map = {"Critical": "#d62728", "High": "#ff7f0e", "Medium": "#ffdd57", "Low": "#2ca02c"}
        fig = px.bar(
            top10,
            x="cve_id",
            y="risk_score",
            color="risk_band" if "risk_band" in top10.columns else None,
            color_discrete_map=color_map,
            labels={"cve_id": "CVE ID", "risk_score": "Contextual Risk Score"},
            title="Top 10 CVEs — Contextual Risk Score",
            text_auto=".3f",
        )
        fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)
    else:
        _render_placeholder_chart()


def _render_placeholder_chart() -> None:
    """Render a sample placeholder chart when no real data is loaded."""
    sample_data = pd.DataFrame(
        {
            "cve_id": [f"CVE-2024-{1000 + i}" for i in range(10)],
            "risk_score": [0.95, 0.88, 0.82, 0.76, 0.71, 0.65, 0.58, 0.49, 0.41, 0.33],
            "risk_band": ["Critical"] * 3 + ["High"] * 3 + ["Medium"] * 2 + ["Low"] * 2,
        }
    )
    color_map = {"Critical": "#d62728", "High": "#ff7f0e", "Medium": "#ffdd57", "Low": "#2ca02c"}
    fig = px.bar(
        sample_data,
        x="cve_id",
        y="risk_score",
        color="risk_band",
        color_discrete_map=color_map,
        title="⚠️ Placeholder — No Real Data Loaded",
        text_auto=".2f",
    )
    fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This chart uses placeholder data. Run the pipeline to populate with real CVEs.")
