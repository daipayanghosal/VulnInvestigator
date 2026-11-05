"""
src/dashboard/data_loader.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ensures data is reliably loaded into Streamlit session state across all pages,
regardless of which URL or page is accessed first.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Bridge Streamlit Cloud Secrets into os.environ for seamless cloud access
try:
    if hasattr(st, "secrets"):
        for secret_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
            if secret_name in st.secrets and not os.environ.get(secret_name):
                os.environ[secret_name] = str(st.secrets[secret_name])
except Exception:
    pass

logger = logging.getLogger(__name__)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def ensure_data_loaded() -> None:
    """Load vulnerabilities, assets, logs, and evaluation metrics into st.session_state if missing."""
    db_path = _PROJECT_ROOT / "data" / "processed" / "vulninvestigator.db"
    eval_path = _PROJECT_ROOT / "data" / "processed" / "evaluation_results.json"
    assets_json_path = _PROJECT_ROOT / "data" / "assets" / "asset_inventory.json"

    # 1. Load asset inventory
    if "asset_inventory" not in st.session_state and assets_json_path.exists():
        try:
            with assets_json_path.open(encoding="utf-8") as fh:
                raw_inv = json.load(fh)
                st.session_state["asset_inventory"] = raw_inv.get("assets", [])
        except Exception as exc:
            logger.error("Failed loading asset_inventory.json: %s", exc)

    # 2. Load vulnerabilities from SQLite
    if st.session_state.get("vuln_df") is None and db_path.exists():
        try:
            with sqlite3.connect(str(db_path)) as conn:
                vuln_df = pd.read_sql_query("SELECT * FROM vulnerabilities", conn)
                if not vuln_df.empty:
                    # Normalise column names
                    if "cvss_score" in vuln_df.columns and "cvss_v3_score" not in vuln_df.columns:
                        vuln_df["cvss_v3_score"] = vuln_df["cvss_score"]
                    if "cvss_severity" in vuln_df.columns and "cvss_v3_severity" not in vuln_df.columns:
                        vuln_df["cvss_v3_severity"] = vuln_df["cvss_severity"]

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
            logger.error("Failed loading SQLite database: %s", exc)

    # 3. Load evaluation results
    if "eval_results" not in st.session_state and eval_path.exists():
        try:
            with eval_path.open(encoding="utf-8") as fh:
                st.session_state["eval_results"] = json.load(fh)
        except Exception as exc:
            logger.error("Failed loading evaluation_results.json: %s", exc)
