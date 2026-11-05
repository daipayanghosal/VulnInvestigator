"""
src/dashboard/app.py
~~~~~~~~~~~~~~~~~~~~~
VulnInvestigator — Main Streamlit Application Entry Point.
Redirects to the Overview dashboard page and ensures shared data is loaded.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Ensure the project root is on sys.path when running directly
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.dashboard.data_loader import ensure_data_loaded

# Page configuration — must be called first
st.set_page_config(
    page_title="VulnInvestigator 🔍",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure database, assets, and evaluation metrics are loaded
ensure_data_loaded()

# Seamlessly navigate to Overview
try:
    st.switch_page("pages/overview.py")
except Exception:
    from src.dashboard.pages import overview
    overview.render()
