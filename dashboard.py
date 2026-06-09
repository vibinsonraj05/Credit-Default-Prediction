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
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%);
        }

        .dashboard-title {
            font-size: 34px;
            font-weight: 800;
            color: #102A43;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }

        .dashboard-subtitle {
            font-size: 15px;
            color: #627D98;
            margin-bottom: 18px;
        }

        .card-box {
            border-radius: 18px;
            padding: 20px 22px;
            background: rgba(255,255,255,0.95);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            transition: all 0.25s ease;
        }

        .card-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.10);
        }

        .metric-title {
            font-size: 13px;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 22px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.2;
        }

        .section-title {
            font-size: 18px;
            font-weight: 800;
            color: #102A43;
            margin-bottom: 10px;
        }

        .profile-item {
            font-size: 15px;
            color: #334E68;
            margin-bottom: 10px;
        }

        .risk-badge {
            display: inline-block;
            padding: 10px 16px;
            border-radius: 999px;
            font-weight: 800;
            font-size: 16px;
            margin-top: 10px;
        }

        .risk-high { color: #B42318; background: #FEE4E2; }
        .risk-medium { color: #B54708; background: #FEF0C7; }
        .risk-low { color: #027A48; background: #D1FADF; }

        .fa-label {
            color: #102A43;
            font-weight: 700;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
            background: white;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Account")
        st.write(f"**User:** {user['NAME']}")
        if st.button("Logout 🔒", use_container_width=True, key="logout_btn"):
            logout()

    credit_data = pd.read_csv("Dataset/default of credit card clients.csv")
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "credit_default_model.pkl")
    model = joblib.load(MODEL_PATH)

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

    st.write("")
    st.divider()

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown("<div class='section-title'><i class='fa-solid fa-user'></i> Customer Profile</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-user"></i> Name:</span> {user['NAME']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-envelope"></i> Email:</span> {user['EMAIL']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-id-card"></i> Card No:</span> {user['CARD_NO']}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-building-columns"></i> Account No:</span> {user['ACCOUNT_NO']}</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-title'><i class='fa-solid fa-chart-line'></i> Risk Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-bolt"></i> Prediction:</span> {"Default" if prediction == 1 else "No Default"}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid fa-percent"></i> Probability:</span> {probability:.2%}</div>
            <div class="profile-item"><span class="fa-label"><i class="fa-solid {icon}"></i> Risk Level:</span></div>
            <div class="risk-badge {risk_class}">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.divider()

    st.markdown("<div class='section-title'><i class='fa-solid fa-coins'></i> Financial Insights</div>", unsafe_allow_html=True)

    summary = pd.DataFrame({
        "Metric": ["Credit Limit", "Total Bill", "Total Payment", "Payment Ratio", "Avg Delay"],
        "Value": [
            f"₹ {customer['LIMIT_BAL'].iloc[0]:,.0f}",
            f"₹ {customer['TOTAL_BILL'].iloc[0]:,.0f}",
            f"₹ {customer['TOTAL_PAYMENT'].iloc[0]:,.0f}",
            f"{customer['PAYMENT_RATIO'].iloc[0]:.2f}",
            f"{customer['AVG_DELAY'].iloc[0]:.2f}"
        ]
    })

    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption("🔐 Secure ML-powered credit risk evaluation system")