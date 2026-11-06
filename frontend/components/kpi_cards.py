"""
KPI Cards and Summary components.
"""
from typing import Dict, Any
import streamlit as st


def render_summary_row(user_meta: Dict[str, Any], risk_data: Dict[str, Any]) -> None:
    """Render the top 3 executive summary cards: Profile, Risk Status, and Financial Snapshot."""
    col_prof, col_risk, col_fin = st.columns([1.1, 1.1, 1.1], gap="medium")

    with col_prof:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">👤 Customer Profile</div>
            <div class="profile-row">
                <span class="profile-label">Full Name</span>
                <span class="profile-value">{user_meta.get('NAME')}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">Customer ID</span>
                <span class="profile-value">#{user_meta.get('ID')}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">Card Number</span>
                <span class="profile-value">{user_meta.get('CARD_NO')}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">Account No</span>
                <span class="profile-value">{user_meta.get('ACCOUNT_NO')}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">Email</span>
                <span class="profile-value" style="font-size:11px;">{user_meta.get('EMAIL')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_risk:
        prob = risk_data["probability"]
        level = risk_data["risk_level"]
        badge_cls = f"risk-{level.lower()}"
        icon = risk_data["risk_icon"]
        thresh = risk_data["threshold"]

        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">🛡️ Risk Intelligence</div>
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:4px;">
                <div class="card-primary-value" style="color:{risk_data['risk_color']};">
                    {prob:.1%}
                </div>
                <div>
                    <span class="risk-pill {badge_cls}">{icon} {level}</span>
                </div>
            </div>
            <div class="card-subtitle" style="margin-bottom:12px;">
                Prediction: <strong>{risk_data['prediction_label']}</strong>
            </div>
            <div class="profile-row">
                <span class="profile-label">Tuned Threshold</span>
                <span class="profile-value">{thresh:.2f}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">Model Pipeline</span>
                <span class="profile-value" style="font-size:11px;">RF + SMOTE</span>
            </div>
            <div style="font-size:11px; color:#64748B; margin-top:8px; line-height:1.4;">
                {risk_data['risk_description']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_fin:
        limit = risk_data["limit_bal"]
        bill = risk_data["total_bill"]
        pay = risk_data["total_payment"]
        ratio = risk_data["payment_ratio"]
        delay = risk_data["avg_delay"]

        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">💰 Financial Snapshot</div>
            <div class="profile-row">
                <span class="profile-label">💳 Credit Limit</span>
                <span class="profile-value">₹ {limit:,.0f}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">🧾 6-Mo Total Bill</span>
                <span class="profile-value">₹ {bill:,.0f}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">💸 6-Mo Total Payment</span>
                <span class="profile-value">₹ {pay:,.0f}</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">⚖️ Payment Ratio</span>
                <span class="profile-value">{ratio:.2f}x</span>
            </div>
            <div class="profile-row">
                <span class="profile-label">⏱️ Avg Repayment Delay</span>
                <span class="profile-value">{delay:.2f} mo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_metric_grid(risk_data: Dict[str, Any]) -> None:
    """Render 4 metric cards for Credit Limit, Total Payment, Total Bill, and Utilization."""
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    limit = risk_data["limit_bal"]
    payment = risk_data["total_payment"]
    bill = risk_data["total_bill"]
    util_pct = risk_data["utilization_pct"]

    if util_pct > 70:
        util_color = "#EF4444"
        util_status = "⚠️ Critical Utilization (>70%)"
    elif util_pct > 40:
        util_color = "#F59E0B"
        util_status = "⚡ Moderate Utilization (40-70%)"
    else:
        util_color = "#10B981"
        util_status = "✅ Healthy Utilization (≤40%)"

    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">💳 Total Credit Limit</div>
            <div class="card-primary-value">₹ {limit:,.0f}</div>
            <div class="card-subtitle">Maximum revolving credit line</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">💸 Total Repayments</div>
            <div class="card-primary-value">₹ {payment:,.0f}</div>
            <div class="card-subtitle">Cumulative payments (6 mos)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">🧾 Cumulative Statement Bill</div>
            <div class="card-primary-value">₹ {bill:,.0f}</div>
            <div class="card-subtitle">Aggregated billed liabilities</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header-title">📊 Revolving Utilization</div>
            <div class="card-primary-value" style="color: {util_color};">{util_pct:.1f}%</div>
            <div class="progress-track">
                <div class="progress-fill" style="width: {util_pct}%; background-color: {util_color};"></div>
            </div>
            <div class="card-subtitle" style="margin-top:8px;">{util_status}</div>
        </div>
        """, unsafe_allow_html=True)
