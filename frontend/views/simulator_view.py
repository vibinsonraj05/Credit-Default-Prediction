"""
What-If Credit Simulator View.
Provides interactive simulation of financial adjustments to evaluate real-time impact on default risk.
"""
from typing import Dict, Any
import streamlit as st

from backend.services.data_service import get_customer_by_id
from backend.services.ml_service import predict_customer_risk, simulate_what_if_scenario
from frontend.components.header import render_top_header
from frontend.components.charts import build_probability_gauge, build_utilization_gauge


def render_simulator_view(active_user: Dict[str, Any]) -> None:
    """Render the What-If financial simulation workspace."""
    customer_id = active_user.get("ID")
    customer_record = get_customer_by_id(customer_id)

    if customer_record is None:
        st.error(f"Customer #{customer_id} record not found.")
        return

    # Baseline evaluation
    baseline = predict_customer_risk(customer_record)

    render_top_header(active_user=active_user, risk_level=baseline["risk_level"])

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-size:22px; font-weight:800; color:#0F172A; margin:0 0 6px 0;">
            🔮 Interactive "What-If" Credit Scenario Simulator
        </h2>
        <p style="font-size:13px; color:#64748B; margin:0;">
            Simulate prospective repayment adjustments, credit limit expansions, or delinquency resolutions to observe real-time AI risk recalculations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Simulator Controls + Output layout
    col_controls, col_results = st.columns([1.1, 1.2], gap="large")

    with col_controls:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header-title'>🎛️ Simulation Parameters</div>", unsafe_allow_html=True)

        current_bill = baseline["bill_history"][0]
        st.write(f"**Current Month 1 Bill Liability:** ₹ {current_bill:,.0f}")
        st.write(f"**Current Credit Limit:** ₹ {baseline['limit_bal']:,.0f}")

        st.markdown("---")

        # Parameter 1: Additional Payment
        add_payment = st.slider(
            "Allocate Extra Payment Toward Month 1 (₹)",
            min_value=0,
            max_value=max(50000, int(current_bill * 1.5)),
            value=min(15000, int(current_bill * 0.5)),
            step=2500,
            format="₹ %d"
        )

        # Parameter 2: Credit Limit Adjustment
        limit_multiplier = st.select_slider(
            "Adjust Revolving Credit Line",
            options=[0.75, 1.0, 1.25, 1.5, 2.0],
            value=1.0,
            format_func=lambda x: f"{x}x (₹ {baseline['limit_bal']*x:,.0f})"
        )

        # Parameter 3: Delay status shift
        delay_shift = st.radio(
            "Delinquency Status Shift",
            options=[-2, -1, 0, 1],
            index=2,
            format_func=lambda x: "On-time Shift (-2 Months)" if x == -2 else "1-Month Improvement (-1 Month)" if x == -1 else "No Change (Baseline)" if x == 0 else "1-Month Late (+1 Month)",
            horizontal=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # Execute simulation
    simulated = simulate_what_if_scenario(
        base_customer_row=customer_record,
        additional_payment=float(add_payment),
        credit_limit_multiplier=float(limit_multiplier),
        delay_adjustment=int(delay_shift)
    )

    with col_results:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header-title'>📊 Simulated Risk Outcome</div>", unsafe_allow_html=True)

        # Side by Side comparison
        sub_c1, sub_c2 = st.columns(2)

        with sub_c1:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Baseline Risk</div>
                <div style="font-size:26px; font-weight:800; color:{baseline['risk_color']}; font-family:'JetBrains Mono'; margin:4px 0;">
                    {baseline['probability']:.1%}
                </div>
                <span class="risk-pill risk-{baseline['risk_level'].lower()}">{baseline['risk_level']}</span>
            </div>
            """, unsafe_allow_html=True)

        with sub_c2:
            prob_diff = simulated["probability"] - baseline["probability"]
            diff_text = f"{prob_diff:+.1%}"
            diff_color = "#10B981" if prob_diff <= 0 else "#EF4444"

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Simulated Risk</div>
                <div style="font-size:26px; font-weight:800; color:{simulated['risk_color']}; font-family:'JetBrains Mono'; margin:4px 0;">
                    {simulated['probability']:.1%}
                </div>
                <span class="risk-pill risk-{simulated['risk_level'].lower()}">{simulated['risk_level']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; margin-top:14px; padding:10px; border-radius:8px; background:#F1F5F9;">
            <span style="font-size:13px; font-weight:600; color:#334E68;">Net Default Probability Delta: </span>
            <strong style="font-size:16px; color:{diff_color}; font-family:'JetBrains Mono';">{diff_text}</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Simulation Key Metrics comparison
        st.markdown(f"""
        <div class="profile-row">
            <span class="profile-label">Simulated Credit Limit</span>
            <span class="profile-value">₹ {simulated['limit_bal']:,.0f}</span>
        </div>
        <div class="profile-row">
            <span class="profile-label">Simulated Total Payment</span>
            <span class="profile-value">₹ {simulated['total_payment']:,.0f}</span>
        </div>
        <div class="profile-row">
            <span class="profile-label">Simulated Utilization</span>
            <span class="profile-value">{simulated['utilization_pct']:.1f}%</span>
        </div>
        <div class="profile-row">
            <span class="profile-label">Simulated Payment Ratio</span>
            <span class="profile-value">{simulated['payment_ratio']:.2f}x</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Gauges for the simulated scenario
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    g1, g2 = st.columns(2, gap="medium")

    with g1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_sim_prob = build_probability_gauge(simulated["probability"], simulated["threshold"])
        st.plotly_chart(fig_sim_prob, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with g2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig_sim_util = build_utilization_gauge(simulated["utilization_pct"])
        st.plotly_chart(fig_sim_util, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
