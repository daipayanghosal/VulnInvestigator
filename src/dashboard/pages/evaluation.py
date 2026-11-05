"""
src/dashboard/pages/evaluation.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluation page — ranking metric charts and evidence grounding analysis.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render() -> None:
    """Render the Evaluation metrics page."""
    st.title("📈 Evaluation")
    st.markdown(
        "Quantitative evaluation of the ranking methodology and AI output quality.  "
        "Run `scripts/run_evaluation.py` to populate metrics."
    )

    eval_results: dict | None = st.session_state.get("eval_results")

    # ----------------------------------------------------------------
    # Kendall tau
    # ----------------------------------------------------------------
    st.subheader("📐 Kendall's τ — Ranking Agreement")
    st.markdown(
        "Measures agreement between CVSS-only and contextual risk rankings.  "
        "τ = 1.0 → identical; τ = −1.0 → reversed; τ ≈ 0 → no correlation."
    )

    if eval_results and "kendall_tau" in eval_results:
        tau = eval_results["kendall_tau"]
        st.metric("Kendall's τ", f"{tau:.4f}")
        _gauge_chart(tau, title="Kendall's τ", low=-1.0, high=1.0)
    else:
        st.info("No evaluation results found. Run `scripts/run_evaluation.py`.")
        _gauge_chart(0.0, title="Kendall's τ (placeholder)", low=-1.0, high=1.0)

    st.divider()

    # ----------------------------------------------------------------
    # Rank displacement distribution
    # ----------------------------------------------------------------
    st.subheader("📊 Rank Displacement Distribution")
    disp_data = (
        eval_results.get("rank_displacement")
        if eval_results
        else None
    ) or (
        eval_results.get("top_displacement")
        if eval_results
        else None
    )
    if disp_data:
        disp_df = pd.DataFrame(disp_data)
        fig = px.histogram(
            disp_df, x="displacement", nbins=30,
            title="Distribution of Rank Displacement (CVSS rank − Contextual rank)",
            labels={"displacement": "Rank Displacement"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Placeholder
        import numpy as np  # type: ignore
        sample_disp = pd.DataFrame({"displacement": np.random.normal(0, 15, 200).astype(int)})
        fig = px.histogram(
            sample_disp, x="displacement", nbins=30,
            title="⚠️ Placeholder — Rank Displacement Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Placeholder data. Run the evaluation script to populate.")

    st.divider()

    # ----------------------------------------------------------------
    # Evidence citation rate
    # ----------------------------------------------------------------
    st.subheader("📌 AI Evidence Grounding Metrics")
    col1, col2, col3 = st.columns(3)

    if eval_results and "evidence_citation_rate" in eval_results:
        col1.metric("Evidence Citation Rate", f"{eval_results['evidence_citation_rate']:.1%}")
        col2.metric("Claim Support Rate", f"{eval_results.get('claim_support_rate', 0):.1%}")
        col3.metric("Hallucination Rate", f"{eval_results.get('hallucination_rate', 0):.1%}")
    else:
        col1.metric("Evidence Citation Rate", "—")
        col2.metric("Claim Support Rate", "—")
        col3.metric("Hallucination Rate", "—")
        st.info("Run the evaluation pipeline to compute grounding metrics.")

    st.divider()

    # ----------------------------------------------------------------
    # Failure mode taxonomy
    # ----------------------------------------------------------------
    st.subheader("🧪 Failure Mode Taxonomy")
    st.markdown(
        "Categories of failure observed during automated testing of the AI pipeline."
    )

    if eval_results and "failure_modes" in eval_results:
        fm_df = pd.DataFrame(eval_results["failure_modes"])
        fig = px.bar(fm_df, x="mode", y="count", title="Failure Mode Counts")
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Placeholder taxonomy
        placeholder_fm = pd.DataFrame(
            {
                "mode": [
                    "Missing CVSS handled",
                    "Missing asset handled",
                    "Contradictory logs handled",
                    "Misleading input handled",
                ],
                "count": [0, 0, 0, 0],
                "status": ["Not tested"] * 4,
            }
        )
        st.dataframe(placeholder_fm, use_container_width=True, hide_index=True)
        st.caption("Run `FailureTester.run_all()` via the evaluation script to populate.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _gauge_chart(value: float, title: str, low: float = 0.0, high: float = 1.0) -> None:
    """Render a Plotly gauge indicator."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            gauge={
                "axis": {"range": [low, high]},
                "bar": {"color": "#1f77b4"},
                "steps": [
                    {"range": [low, (high - low) * 0.33 + low], "color": "#ffcccc"},
                    {"range": [(high - low) * 0.33 + low, (high - low) * 0.66 + low], "color": "#fff9c4"},
                    {"range": [(high - low) * 0.66 + low, high], "color": "#d4edda"},
                ],
            },
        )
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
