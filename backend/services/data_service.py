"""
Data Access and Ingestion Service.
Provides robust cached data loading for credentials, transaction histories, and risk reports.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

try:
    import streamlit as st
    cache_data_decorator = st.cache_data(show_spinner=False)
except ImportError:
    def cache_data_decorator(f):
        return f

from backend.config import CREDENTIALS_PATH, CREDIT_DATA_PATH, RISK_REPORT_PATH


@cache_data_decorator
def load_credentials_df() -> pd.DataFrame:
    """Load credentials dataset with formatted card and account numbers."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Credentials dataset not found at {CREDENTIALS_PATH}")
    
    df = pd.read_csv(
        CREDENTIALS_PATH,
        dtype={"CARD_NO": str, "ACCOUNT_NO": str, "ID": int}
    )
    return df


@cache_data_decorator
def load_credit_dataset() -> pd.DataFrame:
    """Load raw credit card clients dataset."""
    if not CREDIT_DATA_PATH.exists():
        raise FileNotFoundError(f"Credit dataset not found at {CREDCREDIT_DATA_PATH}")
    
    df = pd.read_csv(CREDIT_DATA_PATH)
    return df


@cache_data_decorator
def load_customer_risk_report() -> Optional[pd.DataFrame]:
    """Load precomputed test set customer risk evaluation report if available."""
    if RISK_REPORT_PATH.exists():
        return pd.read_csv(RISK_REPORT_PATH)
    return None


def get_customer_by_id(customer_id: int) -> Optional[pd.Series]:
    """Retrieve credit record row for a given customer ID."""
    df = load_credit_dataset()
    match = df[df["ID"] == customer_id]
    if match.empty:
        return None
    return match.iloc[0]


def get_all_customers_summary() -> pd.DataFrame:
    """Return summary metadata of all clients for admin/exploratory views."""
    df = load_credit_dataset()
    summary = df[["ID", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"]].copy()
    return summary
