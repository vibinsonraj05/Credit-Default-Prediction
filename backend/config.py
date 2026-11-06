"""
Configuration module for Credit Risk Intelligence Platform.
Centralizes paths, model hyperparameters, risk classifications, and presets.
"""
from pathlib import Path
from typing import Dict, Any

# Root project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Backend paths
BACKEND_DIR = BASE_DIR / "backend"
MODELS_DIR = BACKEND_DIR / "models"
REPORTS_DIR = BACKEND_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Frontend paths
FRONTEND_DIR = BASE_DIR / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"
COMPONENTS_DIR = FRONTEND_DIR / "components"
VIEWS_DIR = FRONTEND_DIR / "views"

# Data paths with multi-location fallback
def resolve_file(*candidates: Path) -> Path:
    """Return the first candidate path that exists, or the first candidate if none exist."""
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

CREDENTIALS_PATH = resolve_file(
    BASE_DIR / "data" / "raw" / "Credentials.csv",
    BASE_DIR / "Dataset" / "Credentials.csv",
    BASE_DIR / "Credentials.csv"
)

CREDIT_DATA_PATH = resolve_file(
    BASE_DIR / "data" / "raw" / "default of credit card clients.csv",
    BASE_DIR / "Dataset" / "default of credit card clients.csv",
    BASE_DIR / "default of credit card clients.csv"
)

MODEL_PATH = resolve_file(
    MODELS_DIR / "credit_default_model.pkl",
    BASE_DIR / "credit_default_model.pkl"
)

SCALER_PATH = resolve_file(
    MODELS_DIR / "scaler.pkl",
    BASE_DIR / "scaler.pkl"
)

FEATURE_COLUMNS_PATH = resolve_file(
    MODELS_DIR / "feature_columns.pkl",
    BASE_DIR / "feature_columns.pkl"
)

RISK_REPORT_PATH = resolve_file(
    REPORTS_DIR / "customer_risk_report.csv",
    BASE_DIR / "customer_risk_report.csv"
)

# Application Metadata
APP_NAME = "Credit Risk Intelligence Platform"
APP_SUBTITLE = "Enterprise Machine Learning Risk Assessment & Predictive Analytics"
APP_VERSION = "2.4.0"
APP_AUTHOR = "Vibinson Raj G"

# ML Model Configuration
DEFAULT_OPTIMAL_THRESHOLD = 0.45
HIGH_RISK_THRESHOLD = 0.70

FEATURE_COLUMNS = [
    'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
    'PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
    'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
    'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
    'TOTAL_BILL', 'TOTAL_PAYMENT', 'PAYMENT_RATIO', 'AVG_DELAY', 'UTILIZATION'
]

# Curated Demo Accounts for Instant Review & Testing
DEMO_ACCOUNTS = [
    {
        "id": 7,
        "label": "User 7 - Low Risk Profile (11.2% Default Prob)",
        "email": "user7@gmail.com",
        "password": "WlCg0wdYVB",
        "name": "User_7",
        "badge": "LOW RISK",
        "badge_class": "badge-low"
    },
    {
        "id": 20,
        "label": "User 20 - Medium Risk Profile (50.1% Default Prob)",
        "email": "user20@gmail.com",
        "password": "tt5KDq8Ym4",
        "name": "User_20",
        "badge": "MEDIUM RISK",
        "badge_class": "badge-medium"
    },
    {
        "id": 1,
        "label": "User 1 - High Risk Profile (75.5% Default Prob)",
        "email": "user1@yahoo.com",
        "password": "HRqNUsQcnA",
        "name": "User_1",
        "badge": "HIGH RISK",
        "badge_class": "badge-high"
    }
]
