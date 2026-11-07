"""
app.py
~~~~~~
Root Streamlit entrypoint. Redirects to https://daipayanghosal.github.io/VulnInvestigator/
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.dashboard.redirect import execute_redirect

execute_redirect()
