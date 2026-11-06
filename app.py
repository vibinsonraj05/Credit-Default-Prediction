"""
Credit Risk Intelligence & Default Prediction Platform.
Main Application Entrypoint.
"""
import sys
from pathlib import Path

# Ensure root workspace is on python sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Windows asyncio WinError 10054 connection reset silencer
import backend.patch_asyncio  # noqa: F401

import streamlit as st

# MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Credit Risk Intelligence Platform",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

from backend.services.auth_service import is_authenticated, get_current_user
from frontend.components.sidebar import render_sidebar
from frontend.views.login_view import render_login_view
from frontend.views.dashboard_view import render_dashboard_view
from frontend.views.simulator_view import render_simulator_view
from frontend.views.analytics_view import render_analytics_view


def main():
    # ===== SESSION STATE INITIALIZATION =====
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None

    # ===== ROUTING =====
    if not is_authenticated():
        render_login_view()
    else:
        active_user = get_current_user()
        active_page = render_sidebar(active_user)

        if active_page == "📊 Risk Dashboard":
            render_dashboard_view(active_user)
        elif active_page == "🔮 What-If Simulator":
            render_simulator_view(active_user)
        elif active_page == "📈 Model Governance":
            render_analytics_view(active_user)
        else:
            render_dashboard_view(active_user)


if __name__ == "__main__":
    main()
