"""
Header and Styling injection component.
"""
from pathlib import Path
import streamlit as st
from backend.config import APP_NAME, APP_SUBTITLE, ASSETS_DIR


def inject_custom_styles() -> None:
    """Read style.css and inject it into the Streamlit app DOM."""
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_top_header(active_user: dict = None, risk_level: str = None) -> None:
    """Render top enterprise navbar."""
    inject_custom_styles()

    risk_badge_html = ""
    if risk_level:
        badge_class = f"risk-{risk_level.lower()}"
        icon = "⚠️" if risk_level == "HIGH" else "⚡" if risk_level == "MEDIUM" else "✅"
        risk_badge_html = f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:12px; color:#64748B; font-weight:600;">STATUS:</span>
            <span class="risk-pill {badge_class}">{icon} {risk_level} RISK</span>
        </div>
        """

    user_info_html = ""
    if active_user:
        user_info_html = f"""
        <div style="text-align:right;">
            <div style="font-size:14px; font-weight:700; color:#0F172A;">👤 {active_user.get('NAME', 'User')}</div>
            <div style="font-size:12px; font-weight:500; color:#64748B;">ID: #{active_user.get('ID')} · {active_user.get('EMAIL')}</div>
        </div>
        """

    st.markdown(f"""
    <div class="app-header">
        <div class="app-title-group">
            <h1>💳 {APP_NAME}</h1>
            <p>{APP_SUBTITLE}</p>
        </div>
        <div style="display:flex; align-items:center; gap:20px;">
            {risk_badge_html}
            {user_info_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
