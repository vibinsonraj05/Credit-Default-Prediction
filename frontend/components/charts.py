"""
Plotly Chart Builders for financial timeseries, risk gauges, and delinquency indicators.
"""
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px


def build_bill_vs_payment_chart(months: List[str], bills: List[float], payments: List[float]) -> go.Figure:
    """Grouped bar chart comparing billed liabilities against repayments."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=months,
        y=bills,
        name="Statement Bill",
        marker_color="#2563EB",
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Bill Amount: ₹%{y:,.0f}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=months,
        y=payments,
        name="Repayment Made",
        marker_color="#10B981",
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Payment Amount: ₹%{y:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="<b>6-Month Billing vs Repayment Trajectory</b>",
            font=dict(size=14, family="Inter", color="#0F172A")
        ),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter", size=12, color="#475569"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E2E8F0",
            tickprefix="₹",
            title=dict(text="Amount (INR)", font=dict(size=11))
        ),
        xaxis=dict(
            gridcolor="#F8FAFC",
            title=None
        ),
        height=320
    )
    return fig


def build_delay_trend_chart(months: List[str], delays: List[float]) -> go.Figure:
    """Delinquency trend line chart highlighting on-time vs delayed months."""
    marker_colors = ["#EF4444" if d > 0 else "#10B981" for d in delays]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=months,
        y=delays,
        mode="lines+markers",
        line=dict(color="#F59E0B", width=2.5),
        marker=dict(
            color=marker_colors,
            size=11,
            line=dict(width=2, color="#FFFFFF")
        ),
        name="Delay (Months)",
        fill="tozeroy",
        fillcolor="rgba(245, 158, 11, 0.08)",
        hovertemplate="<b>%{x}</b><br>Delay: %{y} Month(s)<extra></extra>"
    ))

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#94A3B8",
        annotation_text="On-time Baseline (0)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#64748B")
    )

    fig.update_layout(
        title=dict(
            text="<b>Repayment Delay Trend (Delinquency Months)</b>",
            font=dict(size=14, family="Inter", color="#0F172A")
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter", size=12, color="#475569"),
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(
            gridcolor="#F1F5F9",
            zerolinecolor="#E2E8F0",
            title=dict(text="Delay Months", font=dict(size=11))
        ),
        xaxis=dict(
            gridcolor="#F8FAFC",
            title=None
        ),
        height=320
    )
    return fig


def build_utilization_gauge(util_pct: float) -> go.Figure:
    """Radial gauge for revolving credit line utilization percentage."""
    if util_pct > 70:
        bar_color = "#EF4444"
    elif util_pct > 40:
        bar_color = "#F59E0B"
    else:
        bar_color = "#10B981"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=min(util_pct, 100.0),
        title={"text": "<b>Revolving Credit Utilization</b>", "font": {"size": 14, "family": "Inter", "color": "#0F172A"}},
        delta={"reference": 30.0, "suffix": "% vs ideal 30%"},
        number={"suffix": "%", "font": {"size": 28, "family": "JetBrains Mono"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickwidth": 1, "tickcolor": "#94A3B8"},
            "bar": {"color": bar_color, "thickness": 0.28},
            "steps": [
                {"range": [0, 40], "color": "#ECFDF5"},
                {"range": [40, 70], "color": "#FFFBEB"},
                {"range": [70, 100], "color": "#FEF2F2"}
            ],
            "threshold": {
                "line": {"color": "#0F172A", "width": 3},
                "thickness": 0.8,
                "value": util_pct
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=280,
        font=dict(family="Inter", color="#475569"),
        margin=dict(l=24, r=24, t=40, b=10)
    )
    return fig


def build_probability_gauge(prob: float, threshold: float) -> go.Figure:
    """Radial gauge showing predicted probability of default against optimal decision boundary."""
    prob_pct = prob * 100.0
    thresh_pct = threshold * 100.0

    if prob >= 0.70:
        bar_color = "#EF4444"
    elif prob >= threshold:
        bar_color = "#F59E0B"
    else:
        bar_color = "#10B981"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob_pct,
        number={"suffix": "%", "font": {"size": 28, "family": "JetBrains Mono"}},
        title={"text": f"<b>Default Probability (Opt Cutoff: {threshold:.2f})</b>", "font": {"size": 14, "family": "Inter", "color": "#0F172A"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickwidth": 1, "tickcolor": "#94A3B8"},
            "bar": {"color": bar_color, "thickness": 0.28},
            "steps": [
                {"range": [0, thresh_pct], "color": "#ECFDF5"},
                {"range": [thresh_pct, 70], "color": "#FFFBEB"},
                {"range": [70, 100], "color": "#FEF2F2"}
            ],
            "threshold": {
                "line": {"color": "#0F172A", "width": 3},
                "thickness": 0.8,
                "value": thresh_pct
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=280,
        font=dict(family="Inter", color="#475569"),
        margin=dict(l=24, r=24, t=40, b=10)
    )
    return fig
