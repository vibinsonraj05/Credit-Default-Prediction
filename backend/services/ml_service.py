"""
Machine Learning and Predictive Analytics Service.
Handles model serialization, feature engineering pipelines, real-time risk scoring,
and interactive what-if financial simulations.
"""
import warnings
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import joblib

try:
    import streamlit as st
    cache_resource_decorator = st.cache_resource(show_spinner=False)
except ImportError:
    def cache_resource_decorator(f):
        return f

from backend.config import (
    MODEL_PATH,
    SCALER_PATH,
    FEATURE_COLUMNS_PATH,
    DEFAULT_OPTIMAL_THRESHOLD,
    HIGH_RISK_THRESHOLD,
    FEATURE_COLUMNS,
    BASE_DIR
)

# Suppress sklearn unpickle warnings for minor version differences
warnings.filterwarnings("ignore", category=UserWarning)


@cache_resource_decorator
def load_ml_artifacts() -> Tuple[Any, Any, list]:
    """
    Load trained ML model, scaler preprocessor, and feature columns list.
    Cached in memory to eliminate repeated disk I/O latency.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")
    if not SCALER_PATH.exists():
        raise FileNotFoundError(f"Scaler preprocessor not found at {SCALER_PATH}")

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    if FEATURE_COLUMNS_PATH.exists():
        feature_cols = joblib.load(FEATURE_COLUMNS_PATH)
    else:
        feature_cols = FEATURE_COLUMNS

    return model, scaler, feature_cols


def get_optimal_threshold() -> float:
    """Load tuned classification threshold, defaulting to calibrated 0.45."""
    threshold_path = BASE_DIR / "backend" / "models" / "best_threshold.pkl"
    if not threshold_path.exists():
        threshold_path = BASE_DIR / "best_threshold.pkl"

    if threshold_path.exists():
        try:
            return float(joblib.load(threshold_path))
        except Exception:
            pass
    return DEFAULT_OPTIMAL_THRESHOLD


def engineer_features(customer_row: pd.Series) -> pd.DataFrame:
    """
    Apply financial feature engineering to match the training pipeline.
    Computes TOTAL_BILL, TOTAL_PAYMENT, PAYMENT_RATIO, AVG_DELAY, and UTILIZATION.
    """
    df = pd.DataFrame([customer_row.to_dict()])

    bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]
    pay_cols = [f"PAY_AMT{i}" for i in range(1, 7)]
    delay_cols = [f"PAY_{i}" for i in range(1, 7)]

    df["TOTAL_BILL"] = df[bill_cols].sum(axis=1)
    df["TOTAL_PAYMENT"] = df[pay_cols].sum(axis=1)
    df["PAYMENT_RATIO"] = df["TOTAL_PAYMENT"] / (df["TOTAL_BILL"] + 1)
    df["AVG_DELAY"] = df[delay_cols].mean(axis=1)
    df["UTILIZATION"] = df["TOTAL_BILL"] / (df["LIMIT_BAL"] + 1)

    # Ensure all required features are present
    _, _, feature_cols = load_ml_artifacts()
    X = df[feature_cols].copy()
    return X


def evaluate_risk_level(probability: float, threshold: float = None) -> Dict[str, str]:
    """Classify probability into risk tiers and provide display metadata."""
    if threshold is None:
        threshold = get_optimal_threshold()

    if probability >= HIGH_RISK_THRESHOLD:
        return {
            "level": "HIGH",
            "class": "risk-high",
            "icon": "⚠️",
            "color": "#EF4444",
            "description": "High likelihood of delinquency within subsequent billing periods. Immediate intervention recommended."
        }
    elif probability >= threshold:
        return {
            "level": "MEDIUM",
            "class": "risk-medium",
            "icon": "⚡",
            "color": "#F59E0B",
            "description": "Moderate risk profile. Increased monitoring and credit line vigilance advised."
        }
    else:
        return {
            "level": "LOW",
            "class": "risk-low",
            "icon": "✅",
            "color": "#10B981",
            "description": "Healthy repayment behavior. Customer demonstrates low probability of default."
        }


def predict_customer_risk(customer_row: pd.Series) -> Dict[str, Any]:
    """
    Execute full inference pipeline for a customer.
    Returns probability, prediction binary, risk categorization, and engineered metrics.
    """
    model, scaler, feature_cols = load_ml_artifacts()
    threshold = get_optimal_threshold()

    # Feature Engineering
    X = engineer_features(customer_row)
    X_scaled = scaler.transform(X)

    # Predict Probability
    prob = float(model.predict_proba(X_scaled)[0][1])
    is_default = int(prob >= threshold)
    risk_meta = evaluate_risk_level(prob, threshold)

    # Financial Summary Metrics
    limit_bal = float(customer_row["LIMIT_BAL"])
    total_bill = float(X["TOTAL_BILL"].iloc[0])
    total_payment = float(X["TOTAL_PAYMENT"].iloc[0])
    payment_ratio = float(X["PAYMENT_RATIO"].iloc[0])
    avg_delay = float(X["AVG_DELAY"].iloc[0])
    utilization = float(X["UTILIZATION"].iloc[0])
    util_pct = min(max(utilization * 100.0, 0.0), 100.0)

    # 6-Month Timeseries breakdown
    months = ["Month 1 (Sep)", "Month 2 (Aug)", "Month 3 (Jul)", "Month 4 (Jun)", "Month 5 (May)", "Month 6 (Apr)"]
    bill_history = [float(customer_row[f"BILL_AMT{i}"]) for i in range(1, 7)]
    payment_history = [float(customer_row[f"PAY_AMT{i}"]) for i in range(1, 7)]
    delay_history = [float(customer_row[f"PAY_{i}"]) for i in range(1, 7)]

    return {
        "probability": prob,
        "is_default": is_default,
        "prediction_label": "Default Predicted" if is_default == 1 else "No Default Predicted",
        "threshold": threshold,
        "risk_level": risk_meta["level"],
        "risk_class": risk_meta["class"],
        "risk_icon": risk_meta["icon"],
        "risk_color": risk_meta["color"],
        "risk_description": risk_meta["description"],
        "limit_bal": limit_bal,
        "total_bill": total_bill,
        "total_payment": total_payment,
        "payment_ratio": payment_ratio,
        "avg_delay": avg_delay,
        "utilization_pct": util_pct,
        "months": months,
        "bill_history": bill_history,
        "payment_history": payment_history,
        "delay_history": delay_history,
        "model_name": "Random Forest (GridSearchCV Tuned)",
        "balancing_method": "SMOTE (Synthetic Minority Over-sampling)"
    }


def simulate_what_if_scenario(
    base_customer_row: pd.Series,
    additional_payment: float = 0.0,
    credit_limit_multiplier: float = 1.0,
    delay_adjustment: int = 0
) -> Dict[str, Any]:
    """
    Simulate what happens to default risk when financial behaviors change:
    - additional_payment: extra funds allocated to Month 1 payment
    - credit_limit_multiplier: factor scaling the customer's credit limit
    - delay_adjustment: shift in repayment status (e.g. -1 for earlier payment)
    """
    modified = base_customer_row.copy()

    # Adjust Credit Limit
    modified["LIMIT_BAL"] = max(1000.0, modified["LIMIT_BAL"] * credit_limit_multiplier)

    # Adjust Recent Payment
    modified["PAY_AMT1"] = max(0.0, modified["PAY_AMT1"] + additional_payment)

    # Adjust Payment Delay status
    for i in range(1, 7):
        new_val = modified[f"PAY_{i}"] + delay_adjustment
        modified[f"PAY_{i}"] = max(-2, min(8, new_val))

    # Re-evaluate
    return predict_customer_risk(modified)
