"""
Model Analytics and Governance View.
Presents machine learning evaluation metrics, ROC curves, confusion matrices, and feature importance.
"""
from typing import Dict, Any
from pathlib import Path
import streamlit as st
import pandas as pd

from backend.config import ASSETS_DIR, FIGURES_DIR
from backend.services.data_service import load_customer_risk_report
from frontend.components.header import render_top_header


def render_analytics_view(active_user: Dict[str, Any]) -> None:
    """Render ML performance, model comparison, and governance dashboards."""
    render_top_header(active_user=active_user)

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-size:22px; font-weight:800; color:#0F172A; margin:0 0 6px 0;">
            📈 Machine Learning Model Governance & Analytics
        </h2>
        <p style="font-size:13px; color:#64748B; margin:0;">
            Rigorous evaluation benchmarks, cross-model comparison, SMOTE balancing validation, and feature attribution explainability.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Top Model Spec Badges
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header-title'>🔬 Production Architecture Overview</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div style="font-size:11px; color:#64748B; font-weight:700;">CHAMPION MODEL</div>
        <div style="font-size:18px; font-weight:800; color:#0F172A; margin-top:2px;">Random Forest</div>
        <div style="font-size:11px; color:#10B981; font-weight:600;">GridSearchCV Tuned</div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div style="font-size:11px; color:#64748B; font-weight:700;">DATA BALANCING</div>
        <div style="font-size:18px; font-weight:800; color:#0F172A; margin-top:2px;">SMOTE</div>
        <div style="font-size:11px; color:#2563EB; font-weight:600;">Minority Synthetic Resampling</div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown("""
        <div style="font-size:11px; color:#64748B; font-weight:700;">OPTIMAL THRESHOLD</div>
        <div style="font-size:18px; font-weight:800; color:#0F172A; margin-top:2px;">0.45 Cutoff</div>
        <div style="font-size:11px; color:#F59E0B; font-weight:600;">Precision/Recall Optimized</div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown("""
        <div style="font-size:11px; color:#64748B; font-weight:700;">TOTAL FEATURES</div>
        <div style="font-size:18px; font-weight:800; color:#0F172A; margin-top:2px;">28 Engineered</div>
        <div style="font-size:11px; color:#6366F1; font-weight:600;">Timeseries + Ratio Metrics</div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Tabbed Model Explanations
    tab_auc, tab_matrices, tab_feat, tab_pop = st.tabs([
        "📊 ROC-AUC Performance",
        "🎯 Confusion Matrices",
        "🔍 Feature Importance",
        "👥 Population Risk Distribution"
    ])

    with tab_auc:
        st.markdown("### ROC Curve Comparison")
        st.markdown("Evaluates discrimination threshold performance across candidate architectures.")
        roc_img = ASSETS_DIR / "roc_curve_comparison.png"
        if not roc_img.exists():
            roc_img = FIGURES_DIR / "roc_curve_comparison.png"
        if roc_img.exists():
            st.image(str(roc_img), caption="Receiver Operating Characteristic (ROC) Comparison", use_container_width=True)

    with tab_matrices:
        st.markdown("### Confusion Matrix Analysis Across Models")
        st.markdown("Comparison between the baseline linear model, ensemble Random Forest, and gradient-boosted trees.")

        col_cm1, col_cm2, col_cm3 = st.columns(3)
        with col_cm1:
            st.write("**Random Forest (Champion)**")
            rf_img = ASSETS_DIR / "confusion_matrix_Random_Forest.png"
            if rf_img.exists():
                st.image(str(rf_img), use_container_width=True)

        with col_cm2:
            st.write("**XGBoost (Tuned)**")
            xgb_img = ASSETS_DIR / "confusion_matrix_XGBoost_(Tuned).png"
            if xgb_img.exists():
                st.image(str(xgb_img), use_container_width=True)

        with col_cm3:
            st.write("**Logistic Regression (Baseline)**")
            lr_img = ASSETS_DIR / "confusion_matrix_Logistic_Regression.png"
            if lr_img.exists():
                st.image(str(lr_img), use_container_width=True)

    with tab_feat:
        st.markdown("### Global Feature Importance")
        st.markdown("Tree Gini impurity reductions identify primary risk drivers (e.g. payment delay status, payment ratios, utilization).")
        fi_img = ASSETS_DIR / "feature_importance.png"
        if not fi_img.exists():
            fi_img = FIGURES_DIR / "feature_importance.png"
        if fi_img.exists():
            st.image(str(fi_img), caption="Random Forest Feature Importance Weights", use_container_width=True)

    with tab_pop:
        st.markdown("### Customer Risk Population Distribution")
        dist_img = ASSETS_DIR / "risk_distribution.png"
        if not dist_img.exists():
            dist_img = FIGURES_DIR / "risk_distribution.png"
        if dist_img.exists():
            st.image(str(dist_img), caption="Test Population Default Probability Distribution", use_container_width=True)

        # Batch Risk Report Data preview
        report_df = load_customer_risk_report()
        if report_df is not None:
            st.markdown("#### Test Population Evaluation Sample (6,000 Customers)")
            st.dataframe(
                report_df.head(20),
                use_container_width=True,
                height=250
            )
