"""
src/dashboard/pages/rankings.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Side-by-side CVSS vs Contextual Risk ranking comparison page.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.custom_cve_form import render_custom_cve_form
from src.dashboard.data_loader import ensure_data_loaded


def render() -> None:
    """Render the Vulnerability Rankings comparison page."""
    ensure_data_loaded()
    st.title("📊 Vulnerability Rankings")
    st.markdown(
        "Compare **CVSS-only baseline** rankings against **contextual risk** rankings.  "
        "The rank displacement table shows how much each CVE moved."
    )

    # ----------------------------------------------------------------
    # Non-Technical & Executive Guide
    # ----------------------------------------------------------------
    with st.expander("💡 Executive & Non-Technical Guide: How to Understand These Rankings", expanded=False):
        st.markdown(
            """
### ⚖️ Plain-English Guide to Vulnerability Prioritization

**Why Two Different Ranking Tables?**
* **🔵 Left Table (CVSS Baseline)**: The *Traditional Industry Standard*. It ranks bugs based purely on theoretical laboratory severity scores (0.0 to 10.0) from software vendors. It assumes worst-case conditions on every machine.
* **🔴 Right Table (Contextual Risk)**: Our *Enterprise-Calibrated Methodology*. It evaluates the exact same flaws through the lens of your actual enterprise environment (combining CVSS, active CISA KEV exploitation, asset criticality, and internet exposure).

---
### 📐 What is "Rank Displacement"?
Rank displacement measures the **difference between where a bug sits on paper vs. where it actually belongs in your fix queue**:
* **🟢 Green (+ Shift) — The Hidden Landmines**: Vulnerabilities with moderate scores (e.g., CVSS 7.2) that traditional tools ignore. Because threat actors are **actively weaponizing them** on your **Internet-facing servers**, our system elevates them to the top of your queue to prevent an immediate breach.
* **🔴 Red (− Shift) — The False Alarms**: Vulnerabilities with scary-looking scores (e.g., CVSS 9.8) that trigger emergency weekend firefighting. Because CISA confirms **zero wild exploits** and the flaw sits on an isolated internal machine, our system de-escalates them so teams can fix them during regular maintenance.
            """
        )

    # ----------------------------------------------------------------
    # Custom / Manual CVE Ingestion
    # ----------------------------------------------------------------
    render_custom_cve_form(title="➕ Ingest Custom / Unlisted CVE into Rankings")

    vuln_df: pd.DataFrame | None = st.session_state.get("vuln_df")

    if vuln_df is None or vuln_df.empty:
        st.info("No data loaded. Run the pipeline and reload.")
        return

    has_contextual = "rank_contextual" in vuln_df.columns
    has_cvss = "rank_cvss" in vuln_df.columns

    if not has_cvss:
        st.warning("CVSS baseline ranking not found. Run `CVSSBaselineScorer` first.")
        return

    # ----------------------------------------------------------------
    # Filters
    # ----------------------------------------------------------------
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        band_options = ["All"] + list(vuln_df["risk_band"].dropna().unique()) if "risk_band" in vuln_df.columns else ["All"]
        selected_band = st.selectbox("Filter by Risk Band", band_options)
    with col_f2:
        kev_filter = st.radio("KEV Status", ["All", "In KEV only", "Not in KEV"], horizontal=True)

    df = vuln_df.copy()
    if selected_band != "All" and "risk_band" in df.columns:
        df = df[df["risk_band"] == selected_band]
    if kev_filter == "In KEV only":
        df = df[df["in_kev"] == True]  # noqa: E712
    elif kev_filter == "Not in KEV":
        df = df[df["in_kev"] == False]  # noqa: E712

    st.caption(f"Showing {len(df)} CVEs after filters.")
    st.divider()

    # ----------------------------------------------------------------
    # Side-by-side ranking tables
    # ----------------------------------------------------------------
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🔵 CVSS Baseline Ranking")
        cvss_cols = [c for c in ["rank_cvss", "cve_id", "cvss_v3_score", "cvss_v3_severity"] if c in df.columns]
        cvss_top = df.sort_values("rank_cvss").head(20)[cvss_cols] if "rank_cvss" in df.columns else df.head(20)
        st.dataframe(cvss_top, use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("🔴 Contextual Risk Ranking")
        if has_contextual:
            ctx_cols = [c for c in ["rank_contextual", "cve_id", "risk_score", "risk_band", "matched_asset_id"] if c in df.columns]
            ctx_top = df.sort_values("rank_contextual").head(20)[ctx_cols]
            # Colour-coded severity
            st.dataframe(
                ctx_top.style.apply(_colour_risk_band, subset=["risk_band"] if "risk_band" in ctx_top.columns else []),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("Contextual ranking not available. Run contextual scorer first.")

    st.divider()

    # ----------------------------------------------------------------
    # Rank displacement
    # ----------------------------------------------------------------
    if has_cvss and has_contextual:
        st.subheader("📐 Rank Displacement (CVSS rank − Contextual rank)")
        disp_df = df[["cve_id", "rank_cvss", "rank_contextual"]].copy()
        disp_df["displacement"] = disp_df["rank_cvss"] - disp_df["rank_contextual"]
        disp_df = disp_df.sort_values("displacement", key=abs, ascending=False).head(20)

        fig = go.Figure(
            go.Bar(
                x=disp_df["cve_id"],
                y=disp_df["displacement"],
                marker_color=["#2ca02c" if d > 0 else "#d62728" for d in disp_df["displacement"]],
                text=disp_df["displacement"],
                textposition="outside",
            )
        )
        fig.update_layout(
            title="Rank Displacement: Positive = moved up in contextual ranking",
            xaxis_tickangle=-45,
            yaxis_title="Rank Change",
            xaxis_title="CVE ID",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Green bars: CVE ranked higher by contextual score than CVSS alone. Red bars: ranked lower.")
        st.info(
            "💡 **Non-Technical Guide to Rank Displacement**:\n\n"
            "• **Green (+ Bars) — Elevated Priority**: These flaws had moderate CVSS scores on paper, but because they reside "
            "on Internet-facing critical assets or are actively weaponized by adversaries (CISA KEV), contextual scoring "
            "escalates them to the top of the remediation queue.\n\n"
            "• **Red (− Bars) — Prevented False Alarms**: These flaws had high theoretical CVSS scores, but have zero observed "
            "wild exploits or sit safely on isolated internal servers. Contextual scoring de-escalates them so teams "
            "avoid burning critical engineering hours on false alarms."
        )


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _colour_risk_band(series: pd.Series) -> list[str]:
    """Return CSS background colour per risk band value."""
    colour_map = {
        "Critical": "background-color: #ffcccc",
        "High": "background-color: #ffe5b4",
        "Medium": "background-color: #fff9c4",
        "Low": "background-color: #d4edda",
    }
    return [colour_map.get(v, "") for v in series]


render()
