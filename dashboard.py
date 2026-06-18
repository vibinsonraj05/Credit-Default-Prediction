import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px

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

        html, body, .stApp {
            font-family: 'Inter', sans-serif;
            background: #F0F4FA;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: #0D1B2A !important;
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        [data-testid="stSidebar"] * { color: #CBD5E1 !important; }
        [data-testid="stSidebar"] strong { color: #F1F5F9 !important; }
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
            width: 100% !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.12) !important;
        }

        /* ── Page header ── */
        .dashboard-title {
            font-size: 26px;
            font-weight: 800;
            color: #0D1B2A;
            letter-spacing: -0.6px;
            line-height: 1.2;
            margin-bottom: 2px;
        }
        .dashboard-subtitle {
            font-size: 13px;
            color: #64748B;
            font-weight: 500;
            margin-bottom: 10px;
        }

        /* ── Cards ── */
        .card-box {
            border-radius: 14px;
            padding: 16px 18px;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
            height: 100%;
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
        .metric-value {
            font-size: 24px;
            font-weight: 800;
            color: #0D1B2A;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.5px;
            line-height: 1.2;
        }
        .metric-sub {
            font-size: 11px;
            color: #94A3B8;
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* ── Section titles ── */
        .section-title {
            font-size: 15px;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 10px;
            margin-top: 4px;
            letter-spacing: -0.2px;
        }

        /* ── Profile items ── */
        .profile-item {
            font-size: 13px;
            color: #334E68;
            margin-bottom: 7px;
            line-height: 1.4;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }
        .fa-label {
            color: #0D1B2A;
            font-weight: 700;
            min-width: 120px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
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

        /* ── Utilization bar ── */
        .util-bar-bg {
            background: #E2E8F0;
            border-radius: 999px;
            height: 8px;
            margin-top: 6px;
            overflow: hidden;
        }
        .util-bar-fill {
            height: 8px;
            border-radius: 999px;
            transition: width 0.6s ease;
        }

        /* ── Threshold info ── */
        .threshold-info {
            font-size: 11px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 6px;
        }

        /* ── Chart section ── */
        .chart-card {
            background: #FFFFFF;
            border-radius: 14px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06);
            padding: 16px 18px;
        }

        /* ── Table ── */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 4px rgba(15,23,42,0.05) !important;
            background: #fff !important;
        }

        hr {
            border: none !important;
            border-top: 1px solid #E2E8F0 !important;
            margin: 12px 0 !important;
        }

        .stCaption {
            font-size: 12px !important;
            color: #94A3B8 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### Account")
        st.write(f"**User:** {user['NAME']}")
        st.markdown("---")
        st.markdown("### Model Info")
        st.write("**Algorithm:** Random Forest")        # updated: was XGBoost
        st.write("**Balanced via:** SMOTE")
        if st.button("Logout 🔒", key="logout_btn"):
            logout()

    # ── Load data & model ──
    credit_data = pd.read_csv("Dataset/default of credit card clients.csv")
    model       = joblib.load("credit_default_model.pkl")   # Random Forest (GridSearchCV tuned)
    scaler      = joblib.load("scaler.pkl")

    # Load tuned threshold (saved during training); fall back to 0.45 if not found
    try:
        best_threshold = joblib.load("best_threshold.pkl")
    except Exception:
        best_threshold = 0.45

    customer = credit_data[credit_data["ID"] == user["ID"]].copy()
    if customer.empty:
        st.error("Customer record not found.")
        return

    # ── Feature Engineering (must match training pipeline) ──
    customer["TOTAL_BILL"] = customer[
        ["BILL_AMT1","BILL_AMT2","BILL_AMT3","BILL_AMT4","BILL_AMT5","BILL_AMT6"]
    ].sum(axis=1)

    customer["TOTAL_PAYMENT"] = customer[
        ["PAY_AMT1","PAY_AMT2","PAY_AMT3","PAY_AMT4","PAY_AMT5","PAY_AMT6"]
    ].sum(axis=1)

    customer["PAYMENT_RATIO"] = customer["TOTAL_PAYMENT"] / (customer["TOTAL_BILL"] + 1)

    customer["AVG_DELAY"] = customer[
        ["PAY_1","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]
    ].mean(axis=1)

    customer["UTILIZATION"] = customer["TOTAL_BILL"] / (customer["LIMIT_BAL"] + 1)

    X_customer = customer.drop(["ID", "dpnm"], axis=1)
    X_scaled   = scaler.transform(X_customer)

    # ── Prediction using tuned threshold ──
    probability = model.predict_proba(X_scaled)[0][1]
    prediction  = int(probability >= best_threshold)

    if probability >= 0.70:
        risk_level = "HIGH"
        risk_class = "risk-high"
        risk_icon  = "⚠️"
    elif probability >= best_threshold:
        risk_level = "MEDIUM"
        risk_class = "risk-medium"
        risk_icon  = "⚡"
    else:
        risk_level = "LOW"
        risk_class = "risk-low"
        risk_icon  = "✅"

    utilization   = customer["UTILIZATION"].iloc[0]
    payment_ratio = customer["PAYMENT_RATIO"].iloc[0]
    avg_delay     = customer["AVG_DELAY"].iloc[0]
    util_pct      = min(utilization * 100, 100)
    util_color    = "#EF4444" if util_pct > 70 else "#F59E0B" if util_pct > 40 else "#10B981"

    # ── Page Header ──
    st.markdown(
        "<div class='dashboard-title'>🛡️ Credit Risk Analytics Dashboard</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='dashboard-subtitle'>ML-powered risk evaluation · SMOTE-balanced Random Forest · GridSearchCV-tuned · Threshold-optimised predictions</div>",
        unsafe_allow_html=True
    )
    st.divider()

    # ── Row 1: Profile | Risk | Financial Insights ──
    col_profile, col_risk, col_insights = st.columns([1.1, 1, 1], gap="medium")

    with col_profile:
        st.markdown("<div class='section-title'>👤 Customer Profile</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label">🪪 Name:</span> {user['NAME']}</div>
            <div class="profile-item"><span class="fa-label">📧 Email:</span> {user['EMAIL']}</div>
            <div class="profile-item"><span class="fa-label">💳 Card No:</span> {user['CARD_NO']}</div>
            <div class="profile-item"><span class="fa-label">🏦 Account No:</span> {user['ACCOUNT_NO']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_risk:
        st.markdown("<div class='section-title'>📊 Risk Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label">⚡ Prediction:</span> {"Default" if prediction == 1 else "No Default"}</div>
            <div class="profile-item"><span class="fa-label">📈 Probability:</span> {probability:.2%}</div>
            <div class="profile-item"><span class="fa-label">🎯 Threshold:</span> {best_threshold:.2f}</div>
            <div class="profile-item"><span class="fa-label">{risk_icon} Risk Level:</span></div>
            <div class="risk-badge {risk_class}">{risk_level}</div>
            <div class="threshold-info">Random Forest · GridSearchCV tuned · SMOTE balanced</div>
        </div>
        """, unsafe_allow_html=True)

    with col_insights:
        st.markdown("<div class='section-title'>💰 Financial Insights</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-box">
            <div class="profile-item"><span class="fa-label">💳 Credit Limit:</span> ₹ {customer['LIMIT_BAL'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label">🧾 Total Bill:</span> ₹ {customer['TOTAL_BILL'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label">💸 Total Payment:</span> ₹ {customer['TOTAL_PAYMENT'].iloc[0]:,.0f}</div>
            <div class="profile-item"><span class="fa-label">⚖️ Pay Ratio:</span> {payment_ratio:.2f}</div>
            <div class="profile-item"><span class="fa-label">⏱️ Avg Delay:</span> {avg_delay:.2f} months</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Row 2: Metric Cards ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title">💳 Credit Limit</div>
            <div class="metric-value">₹ {customer['LIMIT_BAL'].iloc[0]:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title">💸 Total Payment</div>
            <div class="metric-value">₹ {customer['TOTAL_PAYMENT'].iloc[0]:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title">🧾 Total Bill</div>
            <div class="metric-value">₹ {customer['TOTAL_BILL'].iloc[0]:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="card-box">
            <div class="metric-title">📊 Credit Utilization</div>
            <div class="metric-value" style="color:{util_color}">{util_pct:.1f}%</div>
            <div class="util-bar-bg">
                <div class="util-bar-fill" style="width:{util_pct}%; background:{util_color};"></div>
            </div>
            <div class="metric-sub">{"⚠ High — above 70%" if util_pct > 70 else "~ Moderate" if util_pct > 40 else "✓ Healthy"}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Row 3: Charts ──
    st.markdown("<div class='section-title'>📈 Payment & Bill History</div>", unsafe_allow_html=True)

    months     = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
    bill_amts  = [customer[f"BILL_AMT{i}"].iloc[0] for i in range(1, 7)]
    pay_amts   = [customer[f"PAY_AMT{i}"].iloc[0]  for i in range(1, 7)]
    pay_delays = [customer[f"PAY_{i}"].iloc[0]      for i in range(1, 7)]

    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=months, y=bill_amts,
            name="Bill Amount",
            marker_color="#3B82F6",
            opacity=0.85
        ))
        fig1.add_trace(go.Bar(
            x=months, y=pay_amts,
            name="Payment Made",
            marker_color="#10B981",
            opacity=0.85
        ))
        fig1.update_layout(
            title=dict(text="Bill Amount vs Payment Made", font=dict(size=14, family="Inter")),
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", size=12, color="#334E68"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=50, b=10),
            yaxis=dict(gridcolor="#F1F5F9", tickprefix="₹"),
            xaxis=dict(gridcolor="#F1F5F9"),
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        delay_colors = ["#EF4444" if d > 0 else "#10B981" for d in pay_delays]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months, y=pay_delays,
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2.5),
            marker=dict(color=delay_colors, size=10, line=dict(width=2, color="white")),
            name="Delay (months)",
            fill="tozeroy",
            fillcolor="rgba(245,158,11,0.08)"
        ))
        fig2.add_hline(y=0, line_dash="dot", line_color="#94A3B8", annotation_text="On-time")
        fig2.update_layout(
            title=dict(text="Payment Delay Trend (months)", font=dict(size=14, family="Inter")),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", size=12, color="#334E68"),
            margin=dict(l=10, r=10, t=50, b=10),
            yaxis=dict(gridcolor="#F1F5F9", title="Delay (months)"),
            xaxis=dict(gridcolor="#F1F5F9"),
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 4: Utilization Gauge + Risk Probability Gauge ──
    st.markdown("<div class='section-title'>🎯 Risk Gauges</div>", unsafe_allow_html=True)

    gauge_col1, gauge_col2 = st.columns(2, gap="medium")

    with gauge_col1:
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=util_pct,
            title={"text": "Credit Utilization %", "font": {"size": 14, "family": "Inter"}},
            delta={"reference": 30, "suffix": "%"},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": util_color},
                "steps": [
                    {"range": [0,  40], "color": "#D1FAE5"},
                    {"range": [40, 70], "color": "#FEF3C7"},
                    {"range": [70, 100], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "#0D1B2A", "width": 3},
                    "thickness": 0.75,
                    "value": util_pct
                }
            }
        ))
        fig3.update_layout(
            paper_bgcolor="white", height=280,
            font=dict(family="Inter", color="#334E68"),
            margin=dict(l=20, r=20, t=40, b=10)
        )
        st.plotly_chart(fig3, use_container_width=True)

    with gauge_col2:
        prob_color = "#EF4444" if probability >= 0.70 else "#F59E0B" if probability >= best_threshold else "#10B981"
        fig4 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(probability * 100, 1),
            number={"suffix": "%"},
            title={"text": f"Default Probability  (threshold = {best_threshold:.2f})", "font": {"size": 14, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": prob_color},
                "steps": [
                    {"range": [0,  best_threshold * 100], "color": "#D1FAE5"},
                    {"range": [best_threshold * 100, 70], "color": "#FEF3C7"},
                    {"range": [70, 100], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "#0D1B2A", "width": 3},
                    "thickness": 0.75,
                    "value": best_threshold * 100
                }
            }
        ))
        fig4.update_layout(
            paper_bgcolor="white", height=280,
            font=dict(family="Inter", color="#334E68"),
            margin=dict(l=20, r=20, t=40, b=10)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.caption("🔐 Secure ML-powered credit risk evaluation · Random Forest + SMOTE · GridSearchCV-tuned predictions")