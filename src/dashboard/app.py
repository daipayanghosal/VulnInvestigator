"""
src/dashboard/app.py
~~~~~~~~~~~~~~~~~~~~~
VulnInvestigator — Main Streamlit Application Entry Point.

Launch with:
    streamlit run src/dashboard/app.py

Navigation
----------
The app uses st.session_state to track the current page and passes a shared
data context (loaded once from DB / Parquet) to each page renderer.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is on sys.path when running directly
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Page configuration — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="VulnInvestigator 🔍",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Lazy imports (after path fix)
# ---------------------------------------------------------------------------
from src.dashboard.pages import overview, rankings, investigation, ai_assistant, evaluation  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Session state defaults and data loading
# ---------------------------------------------------------------------------
_PAGES = {
    "🏠 Overview": "overview",
    "📊 Vulnerability Rankings": "rankings",
    "🔎 Threat Investigation": "investigation",
    "🤖 AI Assistant": "ai_assistant",
    "📈 Evaluation": "evaluation",
}

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "overview"

def _load_database_data() -> None:
    """Load vulnerabilities, assets, logs, and evaluation metrics into session_state."""
    import json
    import sqlite3
    import pandas as pd

    db_path = _PROJECT_ROOT / "data" / "processed" / "vulninvestigator.db"
    eval_path = _PROJECT_ROOT / "data" / "processed" / "evaluation_results.json"
    assets_json_path = _PROJECT_ROOT / "data" / "assets" / "asset_inventory.json"

    if assets_json_path.exists():
        try:
            with assets_json_path.open(encoding="utf-8") as fh:
                raw_inv = json.load(fh)
                st.session_state["asset_inventory"] = raw_inv.get("assets", [])
        except Exception as exc:
            logger.error("Failed loading asset_inventory.json: %s", exc)

    if db_path.exists():
        try:
            with sqlite3.connect(str(db_path)) as conn:
                vuln_df = pd.read_sql_query("SELECT * FROM vulnerabilities", conn)
                if not vuln_df.empty:
                    # Normalise column names expected by pages
                    if "cvss_score" in vuln_df.columns and "cvss_v3_score" not in vuln_df.columns:
                        vuln_df["cvss_v3_score"] = vuln_df["cvss_score"]
                    if "cvss_severity" in vuln_df.columns and "cvss_v3_severity" not in vuln_df.columns:
                        vuln_df["cvss_v3_severity"] = vuln_df["cvss_severity"]

                    # Compute baseline & contextual rankings safely (handling NaNs)
                    clean_cvss = vuln_df["cvss_v3_score"].fillna(0.0)
                    clean_risk = vuln_df["risk_score"].fillna(0.0)

                    vuln_df["rank_cvss"] = (
                        clean_cvss.rank(ascending=False, method="min").astype(int)
                    )
                    vuln_df["rank_contextual"] = (
                        clean_risk.rank(ascending=False, method="min").astype(int)
                    )
                    vuln_df["rank_displacement"] = vuln_df["rank_cvss"] - vuln_df["rank_contextual"]
                    vuln_df["in_kev"] = vuln_df["in_kev"].astype(bool)

                    st.session_state["vuln_df"] = vuln_df

                assets_df = pd.read_sql_query("SELECT * FROM assets", conn)
                if not assets_df.empty:
                    st.session_state["assets_df"] = assets_df
        except Exception as exc:
            logger.error("Failed loading data from DB: %s", exc)

    if eval_path.exists():
        try:
            with eval_path.open(encoding="utf-8") as fh:
                st.session_state["eval_results"] = json.load(fh)
        except Exception as exc:
            logger.error("Failed loading evaluation_results.json: %s", exc)

if st.session_state.get("vuln_df") is None:
    _load_database_data()

# ---------------------------------------------------------------------------
# Sidebar — navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🔍 VulnInvestigator")
    st.caption("Evidence-Grounded GenAI for Vulnerability Risk")
    st.divider()

    for label, key in _PAGES.items():
        if st.button(label, use_container_width=True, key=f"nav_{key}"):
            st.session_state["current_page"] = key

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        _load_database_data()
        st.rerun()

    st.caption("v0.1.0 · MIT Licence")

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
page = st.session_state["current_page"]

if page == "overview":
    overview.render()
elif page == "rankings":
    rankings.render()
elif page == "investigation":
    investigation.render()
elif page == "ai_assistant":
    ai_assistant.render()
elif page == "evaluation":
    evaluation.render()
else:
    st.error(f"Unknown page: {page}")
