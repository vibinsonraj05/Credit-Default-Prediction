"""
Enterprise Authentication Portal.
Provides professional login authenticated directly against Credentials.csv,
supporting Email, Customer ID, Card Number, and 1-Click Credentials Autofill.
"""
import streamlit as st
import pandas as pd

from backend.services.auth_service import (
    authenticate_user,
    authenticate_by_id,
    login_user,
    get_sample_credentials,
    get_demo_accounts
)
from backend.config import APP_NAME, APP_SUBTITLE
from frontend.components.header import inject_custom_styles


def render_login_view() -> None:
    """Render the enterprise banking login interface."""
    inject_custom_styles()

    # Center column card layout
    col_l, col_center, col_r = st.columns([1, 1.8, 1])

    with col_center:
        # ── Banking Header ──
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 24px; padding-top: 10px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 16px; font-size: 32px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12);">
                💳
            </div>
            <h1 style="font-size: 26px; font-weight: 800; color: #0F172A; margin: 0 0 6px 0; letter-spacing: -0.6px;">
                {APP_NAME}
            </h1>
            <p style="font-size: 13px; color: #64748B; margin: 0; font-weight: 500;">
                {APP_SUBTITLE}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Main Login Card ──
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        st.markdown("""
        <div style="border-bottom: 1px solid #E2E8F0; padding-bottom: 14px; margin-bottom: 18px;">
            <div style="font-size: 16px; font-weight: 700; color: #0F172A;">🔐 Client Sign In</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">
                Enter registered credentials from <code>Credentials.csv</code> to analyze default risk
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabbed interface: Standard Sign In vs Credentials Directory
        tab_login, tab_directory = st.tabs(["🔑 Enter Credentials", "📋 Credentials Directory (Lookup)"])

        with tab_login:
            # Login Form
            with st.form("enterprise_login_form"):
                identifier = st.text_input(
                    "Account Identifier",
                    placeholder="Enter Email (e.g. user7@gmail.com) or Customer ID (e.g. 7)",
                    help="Supports Email ID, Customer ID number, or Card Number registered in Credentials.csv",
                    key="login_identifier_input"
                )

                password = st.text_input(
                    "Security Key / Password",
                    type="password",
                    placeholder="Enter account password",
                    help="Case-sensitive password matching Credentials.csv",
                    key="login_password_input"
                )

                col_chk, col_sub = st.columns([1, 1])
                with col_chk:
                    remember_me = st.checkbox("Keep session active", value=True)

                submit_btn = st.form_submit_button(
                    "🚀 Sign In & Run Risk Analysis",
                    use_container_width=True
                )

                if submit_btn:
                    if not identifier or not password:
                        st.warning("⚠️ Please provide both your Account Identifier and Password.")
                    else:
                        with st.spinner("Verifying credentials against database..."):
                            user_record = authenticate_user(identifier, password)

                        if user_record:
                            login_user(user_record)
                            st.success(f"✅ Authentication verified for {user_record.get('NAME', 'User')}! Loading risk analytics...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please verify your Email/ID and Password against Credentials.csv.")

        with tab_directory:
            st.markdown("""
            <div style="font-size: 12px; color: #64748B; margin-bottom: 10px;">
                Reference accounts from <code>Dataset/Credentials.csv</code> for testing:
            </div>
            """, unsafe_allow_html=True)

            # Curated quick presets
            demos = get_demo_accounts()
            for d in demos:
                col_d_info, col_d_btn = st.columns([2.5, 1.2])
                with col_d_info:
                    st.markdown(f"""
                    <div style="font-size: 12px; padding: 4px 0;">
                        <strong>{d['label']}</strong><br>
                        <span style="font-family:'JetBrains Mono'; color:#475569; font-size:11px;">
                            Email: {d['email']} | Pass: {d['password']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_d_btn:
                    if st.button("Instant Login", key=f"dir_btn_{d['id']}", use_container_width=True):
                        u = authenticate_by_id(d["id"])
                        if u:
                            login_user(u)
                            st.rerun()
                st.markdown("<hr style='margin:4px 0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)

            # Sample Credentials Table from CSV
            with st.expander("🔎 Browse Sample Credentials.csv Entries"):
                sample_df = get_sample_credentials(limit=6)
                st.dataframe(sample_df, use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Trust & Compliance Footer ──
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 16px; margin-top: 18px; font-size: 11px; color: #94A3B8; font-weight: 500;">
            <span>🔒 TLS 1.3 Encrypted</span>
            <span>•</span>
            <span>🛡️ ISO/IEC 27001</span>
            <span>•</span>
            <span>⚡ Calibrated RF Engine</span>
            <span>•</span>
            <span>📄 Synthetic Data</span>
        </div>
        <div style="text-align: center; margin-top: 8px; font-size: 11px; color: #94A3B8;">
            © 2026 Vibinson Raj G · Credit Risk Intelligence Platform
        </div>
        """, unsafe_allow_html=True)
