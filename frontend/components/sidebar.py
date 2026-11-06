"""
Sidebar Navigation and Context component.
"""
from typing import Dict, Any, Tuple
import streamlit as st
from backend.services.auth_service import logout_user, authenticate_by_id, login_user
from backend.config import DEMO_ACCOUNTS, APP_VERSION


def render_sidebar(active_user: Dict[str, Any]) -> str:
    """
    Renders sidebar navigation, profile info, quick switcher, and system status.
    Returns the currently selected view/page name.
    """
    with st.sidebar:
        # Branding Header
        st.markdown(f"""
        <div style="padding: 8px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px;">
            <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
                🛡️ FINTECH RISK AI
            </div>
            <div style="font-size: 11px; color: #94A3B8; font-weight: 500;">
                Enterprise Credit Intelligence v{APP_VERSION}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Main Navigation
        page = st.radio(
            "NAVIGATION",
            options=["📊 Risk Dashboard", "🔮 What-If Simulator", "📈 Model Governance"],
            index=0,
            key="active_nav_tab"
        )

        st.markdown("---")

        # Active Customer Details
        card_raw = str(active_user.get("CARD_NO", ""))
        masked_card = f"•••• {card_raw[-4:]}" if len(card_raw) >= 4 else card_raw

        acc_raw = str(active_user.get("ACCOUNT_NO", ""))
        masked_acc = f"•••• {acc_raw[-4:]}" if len(acc_raw) >= 4 else acc_raw

        st.markdown("### 🪪 Active Profile")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">{active_user.get('NAME')}</div>
            <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">💳 Card: <strong style="color:#CBD5E1;">{masked_card}</strong></div>
            <div style="font-size: 11px; color: #94A3B8;">🏦 Acc: <strong style="color:#CBD5E1;">{masked_acc}</strong></div>
            <div style="font-size: 11px; color: #94A3B8;">📧 Email: <strong style="color:#CBD5E1;">{active_user.get('EMAIL')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        # Quick Switcher for Demo / Evaluator convenience
        st.markdown("### 🔄 Quick Risk Switcher")
        demo_labels = [d["label"] for d in DEMO_ACCOUNTS]
        current_idx = 0
        for idx, d in enumerate(DEMO_ACCOUNTS):
            if d["id"] == active_user.get("ID"):
                current_idx = idx
                break

        selected_demo_label = st.selectbox(
            "Switch Demo Profile",
            options=demo_labels,
            index=current_idx,
            label_visibility="collapsed"
        )

        selected_demo = next((d for d in DEMO_ACCOUNTS if d["label"] == selected_demo_label), None)
        if selected_demo and selected_demo["id"] != active_user.get("ID"):
            if st.button("Apply Profile", key="btn_apply_profile", use_container_width=True):
                new_user = authenticate_by_id(selected_demo["id"])
                if new_user:
                    login_user(new_user)
                    st.rerun()

        st.markdown("---")

        # Model Specs Card
        st.markdown("### ⚙️ Engine Specs")
        st.markdown("""
        <div style="font-size: 11px; color: #94A3B8; line-height: 1.6;">
            <div>• <strong>Algorithm:</strong> Tuned Random Forest</div>
            <div>• <strong>Balancing:</strong> SMOTE Over-sampling</div>
            <div>• <strong>Calibration:</strong> GridSearch Opt</div>
            <div>• <strong>Threshold:</strong> 0.45 Optimized</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Logout button
        if st.button("Sign Out 🔒", key="sidebar_logout_btn", use_container_width=True):
            logout_user()

    return page
