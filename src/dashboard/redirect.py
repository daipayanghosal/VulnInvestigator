"""
src/dashboard/redirect.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Handles seamless redirection from the legacy Streamlit deployment
(https://vulninvestigator.streamlit.app) to the official GitHub Pages
production application (https://daipayanghosal.github.io/VulnInvestigator/).
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

TARGET_URL = "https://daipayanghosal.github.io/VulnInvestigator/"


def execute_redirect(subpath: str = "") -> None:
    """Render client-side auto-redirect to the GitHub Pages production deployment."""
    full_target = f"{TARGET_URL.rstrip('/')}/{subpath.lstrip('/')}" if subpath else TARGET_URL

    try:
        st.set_page_config(
            page_title="VulnInvestigator — Moving to New Platform",
            page_icon="https://daipayanghosal.github.io/VulnInvestigator/favicon.svg",
            layout="centered",
        )
    except Exception:
        pass

    # 1. Immediate JavaScript redirect breaking out of Streamlit iframe
    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta http-equiv="refresh" content="0; url={full_target}">
          <script>
            (function() {{
              try {{
                if (window.top && window.top !== window) {{
                  window.top.location.href = "{full_target}";
                }} else {{
                  window.location.href = "{full_target}";
                }}
              }} catch (e) {{
                window.location.href = "{full_target}";
              }}
            }})();
          </script>
        </head>
        <body></body>
        </html>
        """,
        height=0,
        width=0,
    )

    # 2. Sleek fallback Apple-styled card
    st.markdown(
        f"""
        <style>
          #MainMenu, header, footer {{ visibility: hidden; }}
          .block-container {{ padding-top: 2.5rem; }}
        </style>
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 44px 24px; max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.08);">
          <div style="width: 60px; height: 60px; border-radius: 18px; background: linear-gradient(135deg, #0071E3, #0051A8); margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0, 113, 227, 0.3);">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h2 style="color: #1d1d1f; font-weight: 600; font-size: 22px; margin: 0 0 10px 0; letter-spacing: -0.02em;">VulnInvestigator Has Upgraded</h2>
          <p style="color: #6e6e73; font-size: 14.5px; margin: 0 0 24px 0; line-height: 1.55;">
            VulnInvestigator has transitioned to a new platform on GitHub Pages featuring real-time client-side AI analysis and interactive risk simulations.
          </p>
          <a href="{full_target}" target="_top" style="display: inline-block; background-color: #0071E3; color: white; padding: 12px 32px; border-radius: 980px; text-decoration: none; font-weight: 500; font-size: 15px; box-shadow: 0 4px 14px rgba(0, 113, 227, 0.35);">
            Open New Platform &rarr;
          </a>
          <p style="color: #86868b; font-size: 12px; margin-top: 20px;">
            Redirecting automatically to <a href="{full_target}" target="_top" style="color: #0071E3; text-decoration: underline;">daipayanghosal.github.io/VulnInvestigator</a>...
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
