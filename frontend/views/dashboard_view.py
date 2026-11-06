"""
Executive Dashboard View: Customer profile, risk scoring, financial timeseries,
predictive driver explainability, and comprehensive risk analysis.
"""
from typing import Dict, Any
import streamlit as st
import pandas as pd

from backend.services.data_service import get_customer_by_id
from backend.services.ml_service import predict_customer_risk
from frontend.components.header import render_top_header
from frontend.components.kpi_cards import render_summary_row, render_metric_grid
from frontend.components.charts import (
    build_bill_vs_payment_chart,
    build_delay_trend_chart,
    build_utilization_gauge,
    build_probability_gauge
)


def render_dashboard_view(active_user: Dict[str, Any]) -> None:
    """Render the primary executive credit risk dashboard and deep customer analysis."""
    customer_id = active_user.get("ID")
    customer_record = get_customer_by_id(customer_id)

    if customer_record is None:
        st.error(f"Customer transaction record for ID #{customer_id} could not be located in credit dataset.")
        return

    # Generate ML Prediction and financial analytics
    risk_data = predict_customer_risk(customer_record)

    # 1. Top Navbar
    render_top_header(active_user=active_user, risk_level=risk_data["risk_level"])

    # 2. Executive Summary Row
    render_summary_row(user_meta=active_user, risk_data=risk_data)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 3. Metric KPI Cards Row
    render_metric_grid(risk_data=risk_data)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 4. Deep Risk Analysis & Predictive Driver Attribution
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header-title'>🔬 Predictive Driver Attribution & Risk Diagnostics</div>", unsafe_allow_html=True)

    prob = risk_data["probability"]
    level = risk_data["risk_level"]
    avg_delay = risk_data["avg_delay"]
    ratio = risk_data["payment_ratio"]
    util = risk_data["utilization_pct"]

    col_d1, col_d2, col_d3 = st.columns(3, gap="medium")

    with col_d1:
        if avg_delay <= 0:
            delay_icon, delay_title, delay_badge = "✅", "Punctual Repayment", "Favorable"
            delay_desc = f"Average repayment delay is {avg_delay:.2f} months. Customer has maintained consistent on-time payments across 6 billing cycles."
            delay_box_style = "background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46;"
        elif avg_delay <= 1:
            delay_icon, delay_title, delay_badge = "⚡", "Minor Grace Period Delays", "Caution"
            delay_desc = f"Average repayment delay is {avg_delay:.2f} months. Occasional 30-day delinquency recorded; elevated default probability."
            delay_box_style = "background:#FFFBEB; border:1px solid #FDE68A; color:#92400E;"
        else:
            delay_icon, delay_title, delay_badge = "⚠️", "Chronic Delinquency", "Critical Risk"
            delay_desc = f"Average repayment delay is {avg_delay:.2f} months (>60 days overdue). High correlation with credit default."
            delay_box_style = "background:#FEF2F2; border:1px solid #FECACA; color:#991B1B;"

        st.markdown(f"""
        <div style="{delay_box_style} padding:14px; border-radius:10px; height:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="font-size:13px;">{delay_icon} Repayment Discipline</strong>
                <span style="font-size:10px; font-weight:800; text-transform:uppercase;">{delay_badge}</span>
            </div>
            <div style="font-size:12px; margin-top:8px; line-height:1.4;">{delay_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        if util <= 40:
            util_icon, util_badge = "✅", "Healthy"
            util_desc = f"Credit utilization sits at {util:.1f}% (below 40% benchmark). Customer maintains substantial borrowing reserve."
            util_box_style = "background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46;"
        elif util <= 70:
            util_icon, util_badge = "⚡", "Moderate"
            util_desc = f"Credit utilization is elevated at {util:.1f}%. High revolving balances create vulnerability to liquidity shocks."
            util_box_style = "background:#FFFBEB; border:1px solid #FDE68A; color:#92400E;"
        else:
            util_icon, util_badge = "⚠️", "Over-Leveraged"
            util_desc = f"Credit utilization exceeds danger threshold at {util:.1f}%. Customer has maxed out revolving facilities."
            util_box_style = "background:#FEF2F2; border:1px solid #FECACA; color:#991B1B;"

        st.markdown(f"""
        <div style="{util_box_style} padding:14px; border-radius:10px; height:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="font-size:13px;">{util_icon} Balance Utilization</strong>
                <span style="font-size:10px; font-weight:800; text-transform:uppercase;">{util_badge}</span>
            </div>
            <div style="font-size:12px; margin-top:8px; line-height:1.4;">{util_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_d3:
        if ratio >= 0.8:
            rat_icon, rat_badge = "✅", "Strong Liquidity"
            rat_desc = f"Repayment ratio is {ratio:.2f}x. Customer pays off substantial portions of billed obligations each cycle."
            rat_box_style = "background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46;"
        elif ratio >= 0.3:
            rat_icon, rat_badge = "⚡", "Partial Amortization"
            rat_desc = f"Repayment ratio is {ratio:.2f}x. Customer relies heavily on revolving credit minimum balance rollovers."
            rat_box_style = "background:#FFFBEB; border:1px solid #FDE68A; color:#92400E;"
        else:
            rat_icon, rat_badge = "⚠️", "Insolvent Repayment"
            rat_desc = f"Repayment ratio is critically low at {ratio:.2f}x. Payments represent a negligible fraction of billed liabilities."
            rat_box_style = "background:#FEF2F2; border:1px solid #FECACA; color:#991B1B;"

        st.markdown(f"""
        <div style="{rat_box_style} padding:14px; border-radius:10px; height:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="font-size:13px;">{rat_icon} Payment-to-Bill Ratio</strong>
                <span style="font-size:10px; font-weight:800; text-transform:uppercase;">{rat_badge}</span>
            </div>
            <div style="font-size:12px; margin-top:8px; line-height:1.4;">{rat_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 5. Timeseries Analytics Charts
    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_bar = build_bill_vs_payment_chart(
            risk_data["months"],
            risk_data["bill_history"],
            risk_data["payment_history"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_line = build_delay_trend_chart(
            risk_data["months"],
            risk_data["delay_history"]
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 6. Radial Risk & Utilization Gauges
    gauge_col1, gauge_col2 = st.columns(2, gap="medium")

    with gauge_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_util = build_utilization_gauge(risk_data["utilization_pct"])
        st.plotly_chart(fig_util, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with gauge_col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_prob = build_probability_gauge(risk_data["probability"], risk_data["threshold"])
        st.plotly_chart(fig_prob, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 7. Month-by-Month Statement Audit Ledger
    with st.expander("📑 Detailed 6-Month Billing & Repayment Ledger", expanded=False):
        months_rev = ["Month 1 (Sep)", "Month 2 (Aug)", "Month 3 (Jul)", "Month 4 (Jun)", "Month 5 (May)", "Month 6 (Apr)"]
        audit_rows = []
        for i in range(1, 7):
            b = float(customer_record[f"BILL_AMT{i}"])
            p = float(customer_record[f"PAY_AMT{i}"])
            d = int(customer_record[f"PAY_{i}"])
            status_str = "Paid in Full / Ahead (-1/-2)" if d < 0 else "Paid on time (0)" if d == 0 else f"{d} Month(s) Overdue"
            audit_rows.append({
                "Billing Cycle": months_rev[i-1],
                "Billed Amount (₹)": f"₹ {b:,.2f}",
                "Repayment Made (₹)": f"₹ {p:,.2f}",
                "Net Residual (₹)": f"₹ {max(0.0, b - p):,.2f}",
                "Delinquency Status": status_str
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 8. Actionable Risk Advisory Panel
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header-title'>💡 Automated Advisory & Risk Mitigation Plan</div>", unsafe_allow_html=True)

    if level == "HIGH":
        st.markdown("""
        <div style="background:#FEF2F2; border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 6px;">
            <strong style="color:#991B1B; font-size:14px;">Urgent Risk Containment Required:</strong>
            <ul style="color:#7F1D1D; margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; line-height:1.6;">
                <li><strong>Overdue Status:</strong> Multiple billing cycles show 60+ days payment delays. Default probability is critically elevated at >70%.</li>
                <li><strong>Immediate Mitigation:</strong> Implement an emergency structured debt settlement installment program.</li>
                <li><strong>Line Restrictions:</strong> Freeze temporary credit increases and cap revolving transactions until Month 1 balance is amortized.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif level == "MEDIUM":
        st.markdown("""
        <div style="background:#FFFBEB; border-left: 4px solid #F59E0B; padding: 14px 18px; border-radius: 6px;">
            <strong style="color:#92400E; font-size:14px;">Precautionary Monitoring:</strong>
            <ul style="color:#78350F; margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; line-height:1.6;">
                <li><strong>Borderline Risk:</strong> Default probability is between calibrated threshold (45%) and high risk (70%).</li>
                <li><strong>Mitigation Strategy:</strong> Enroll in automated recurring direct-debit to eliminate recurring 1-month delay penalties.</li>
                <li><strong>Balance Target:</strong> Reducing current revolving balance by 15-20% transitions this profile into the Low-Risk tier.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#ECFDF5; border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 6px;">
            <strong style="color:#065F46; font-size:14px;">Prime Credit Standing:</strong>
            <ul style="color:#064E3B; margin: 8px 0 0 0; padding-left: 20px; font-size: 13px; line-height:1.6;">
                <li><strong>Superb Repayment Track Record:</strong> On-time payments, low revolving utilization, and solid cash flow liquidity.</li>
                <li><strong>Recommended Upsell:</strong> Qualified for pre-approved credit line increases and Tier-1 cashback rewards.</li>
                <li><strong>Maintenance:</strong> Continue maintaining revolving balance below 30% of total credit limit.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 9. Audit & Data Export
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    exp_col1, exp_col2 = st.columns([3, 1])
    with exp_col2:
        export_df = pd.DataFrame([{
            "Customer_ID": customer_id,
            "Name": active_user.get("NAME"),
            "Email": active_user.get("EMAIL"),
            "Credit_Limit": risk_data["limit_bal"],
            "Default_Probability": f"{risk_data['probability']:.4f}",
            "Risk_Tier": risk_data["risk_level"],
            "Prediction": risk_data["prediction_label"],
            "Utilization_Pct": f"{risk_data['utilization_pct']:.2f}%",
            "Payment_Ratio": f"{risk_data['payment_ratio']:.2f}",
            "Avg_Delay_Months": f"{risk_data['avg_delay']:.2f}"
        }])
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Assessment CSV",
            data=csv_data,
            file_name=f"credit_risk_assessment_user_{customer_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
