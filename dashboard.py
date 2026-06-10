import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="Credit Risk Dashboard",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)


def logout():
    st.session_state.clear()
    st.rerun()


def show_dashboard():
    if "user" not in st.session_state:
        st.warning("Please log in first.")
        st.stop()

    user = st.session_state.user

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

        /* ── Base ── */
        html, body, .stApp {
            font-family: 'Inter', sans-serif;
            background: #F0F4FA;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: #0D1B2A !important;
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        [data-testid="stSidebar"] * {
            color: #CBD5E1 !important;
        }
        [data-testid="stSidebar"] strong {
            color: #F1F5F9 !important;
        }
        [data-testid="stSidebar"] h3 {
            color: #94A3B8 !important;
            font-size: 11px !important;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            font-weight: 700 !important;
            margin-bottom: 12px;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.06) !important;
            color: #CBD5E1 !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 8px 14px !important;
            transition: background 0.2s ease;
            width: 100% !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.12) !important;
        }

        /* ── Page header ── */
        .dashboard-title {
            font-size: 24px;
            font-weight: 800;
            color: #0D1B2A;
            letter-spacing: -0.6px;
            line-height: 1.2;
            margin-bottom: 2px;
        }
        .dashboard-title i {
            color: #2563EB;
            margin-right: 10px;
        }
        .dashboard-subtitle {
            font-size: 13px;
            color: #64748B;
            font-weight: 500;
            margin-bottom: 10px;
        }

        /* ── Metric cards ── */
        .card-box {
            border-radius: 14px;
            padding: 16px 18px;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }
        .card-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(15,23,42,0.10);
        }

        .metric-title {
            font-size: 11px;
            color: #94A3B8;
            font-weight: 700;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.9px;
        }
        .metric-title i {
            margin-right: 5px;
            color: #2563EB;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 800;
            color: #0D1B2A;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.5px;
            line-height: 1.2;
        }

        /* ── Section titles ── */
        .section-title {
            font-size: 15px;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 10px;
            letter-spacing: -0.2px;
        }
        .section-title i {
            color: #2563EB;
            margin-right: 7px;
        }

        /* ── Profile & Risk cards ── */
        .profile-item {
            font-size: 13px;
            color: #334E68;
            margin-bottom: 7px;
            line-height: 1.4;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .fa-label {
            color: #0D1B2A;
            font-weight: 700;
            min-width: 110px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .fa-label i {
            color: #2563EB;
            width: 14px;
            text-align: center;
        }

        /* ── Risk badge ── */
        .risk-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 8px 18px;
            border-radius: 999px;
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-top: 8px;
        }
        .risk-high   { color: #991B1B; background: #FEE2E2; border: 1px solid #FECACA; }
        .risk-medium { color: #92400E; background: #FEF3C7; border: 1px solid #FDE68A; }
        .risk-low    { color: #065F46; background: #D1FAE5; border: 1px solid #A7F3D0; }

        /* ── Table ── */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 4px rgba(15,23,42,0.05) !important;
            background: #fff !important;
        }

        /* ── Divider ── */
        hr {
            border: none !important;
            border-top: 1px solid #E2E8F0 !important;
            margin: 12px 0 !important;
        }

        /* ── Caption ── */
        .stCaption {
            font-size: 12px !important;
            color: #94A3B8 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Account")
        st.write(f"**User:** {user['NAME']}")
        if st.button("Logout 🔒", width="stretch", key="logout_btn"):
            logout()

    credit_data = pd.read_csv("Dataset/default of credit card clients.csv")
    model = joblib.load("credit_default_model.pkl")
    scaler = joblib.load("scaler.pkl")

    customer = credit_data[credit_data["ID"] == user["ID"]].copy()
    if customer.empty:
        st.error("Customer record not found")
        return

    customer["TOTAL_BILL"] = customer[
        ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]
    ].sum(axis=1)

    customer["TOTAL_PAYMENT"] = customer[
        ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
    ].sum(axis=1)

    customer["PAYMENT_RATIO"] = customer["TOTAL_PAYMENT"] / (customer["TOTAL_BILL"] + 1)

    customer["AVG_DELAY"] = customer[
        ["PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
    ].mean(axis=1)

    X_customer = customer.drop(["ID", "dpnm"], axis=1)
    X_scaled = scaler.transform(X_customer)

    prediction = model.predict(X_scaled)[0]
    probability = model.predict_proba(X_scaled)[0][1]

    if probability >= 0.70:
        risk_level = "HIGH"
        risk_class = "risk-high"
        icon = "fa-triangle-exclamation"
    elif probability >= 0.40:
        risk_level = "MEDIUM"
        risk_class = "risk-medium"
        icon = "fa-circle-exclamation"
    else:
        risk_level = "LOW"
        risk_class = "risk-low"
        icon = "fa-circle-check"

    st.markdown(
        "<div class='dashboard-title'><i class='fa-solid fa-shield-halved'></i> Credit Risk Analytics Dashboard</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='dashboard-subtitle'>Professional ML-based evaluation of customer financial risk</div>",
        unsafe_allow_html=True
    )
    st.divider()

    # ── Row 1: Profile | Risk | Insights ──
    col_profile, col_risk, col_insights = st.columns([1.1, 1, 1], gap="medium")

    with col_profile:
        st.markdown("<div class='section-title'><i class='fa-solid fa-user'></i> Customer Profile</div>",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-user"></i> Name:</span> {user['NAME']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-envelope"></i> Email:</span> {user['EMAIL']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-id-card"></i> Card No:</span> {user['CARD_NO']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-building-columns"></i> Account No:</span> {user['ACCOUNT_NO']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_risk:
        st.markdown("<div class='section-title'><i class='fa-solid fa-chart-line'></i> Risk Analysis</div>",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-bolt"></i> Prediction:</span> {"Default" if prediction == 1 else "No Default"}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-percent"></i> Probability:</span> {probability:.2%}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid {icon}"></i> Risk Level:</span></div>
            <div class="risk-badge {risk_class}">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_insights:
        st.markdown("<div class='section-title'><i class='fa-solid fa-coins'></i> Financial Insights</div>",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-credit-card"></i> Credit Limit:</span> ₹ {customer['LIMIT_BAL'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-file-invoice-dollar"></i> Total Bill:</span> ₹ {customer['TOTAL_BILL'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-money-bill-wave"></i> Total Payment:</span> ₹ {customer['TOTAL_PAYMENT'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-scale-balanced"></i> Pay Ratio:</span> {customer['PAYMENT_RATIO'].iloc[0]:.2f}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-clock"></i> Avg Delay:</span> {customer['AVG_DELAY'].iloc[0]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Row 2: Metric Cards ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title"><i class="fa-solid fa-credit-card"></i> Credit Limit</div>
            <div class="metric-value">₹ {customer['LIMIT_BAL'].iloc[0]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title"><i class="fa-solid fa-money-bill-wave"></i> Total Payment</div>
            <div class="metric-value">₹ {customer['TOTAL_PAYMENT'].iloc[0]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title"><i class="fa-solid fa-file-invoice-dollar"></i> Total Bill</div>
            <div class="metric-value">₹ {customer['TOTAL_BILL'].iloc[0]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.caption("🔐 Secure ML-powered credit risk evaluation system")
