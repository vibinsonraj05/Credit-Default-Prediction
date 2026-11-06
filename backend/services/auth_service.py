"""
Authentication and User Session Service.
Handles credentials validation directly against Credentials.csv,
supports flexible identification (Email, Customer ID, Card No, Account No),
and manages Streamlit session state.
"""
from typing import Optional, Dict, Any, List
import pandas as pd

try:
    import streamlit as st
except ImportError:
    st = None

from backend.services.data_service import load_credentials_df
from backend.config import DEMO_ACCOUNTS


def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Validate user identifier (Email, Customer ID, Name, Card No, or Account No)
    and Password against Credentials.csv.
    Returns customer metadata dictionary if valid, None otherwise.
    """
    if not identifier or not password:
        return None

    try:
        credentials = load_credentials_df()
        id_clean = str(identifier).strip()
        pw_clean = str(password).strip()

        # 1. Match by EMAIL (case-insensitive)
        matched = credentials[
            (credentials["EMAIL"].astype(str).str.strip().str.lower() == id_clean.lower()) &
            (credentials["PASSWORD"].astype(str).str.strip() == pw_clean)
        ]
        if not matched.empty:
            return matched.iloc[0].to_dict()

        # 2. Match by NAME (e.g. User_7, user_1)
        matched = credentials[
            (credentials["NAME"].astype(str).str.strip().str.lower() == id_clean.lower()) &
            (credentials["PASSWORD"].astype(str).str.strip() == pw_clean)
        ]
        if not matched.empty:
            return matched.iloc[0].to_dict()

        # 3. Match by ID (numeric e.g. 7, 20, 1)
        if id_clean.isdigit():
            matched = credentials[
                (credentials["ID"] == int(id_clean)) &
                (credentials["PASSWORD"].astype(str).str.strip() == pw_clean)
            ]
            if not matched.empty:
                return matched.iloc[0].to_dict()

        # 4. Match by CARD_NO or ACCOUNT_NO (ignoring spaces)
        clean_num = id_clean.replace(" ", "")
        matched = credentials[
            ((credentials["CARD_NO"].astype(str).str.replace(" ", "") == clean_num) |
             (credentials["ACCOUNT_NO"].astype(str).str.replace(" ", "") == clean_num)) &
            (credentials["PASSWORD"].astype(str).str.strip() == pw_clean)
        ]
        if not matched.empty:
            return matched.iloc[0].to_dict()

    except Exception:
        pass

    return None


def authenticate_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Directly fetch user dictionary by Customer ID from Credentials.csv."""
    try:
        credentials = load_credentials_df()
        matched = credentials[credentials["ID"] == int(user_id)]
        if not matched.empty:
            return matched.iloc[0].to_dict()
    except Exception:
        pass
    return None


def get_demo_accounts() -> List[Dict[str, Any]]:
    """Return available pre-configured demo user accounts."""
    return DEMO_ACCOUNTS


def get_sample_credentials(limit: int = 5) -> pd.DataFrame:
    """Return sample formatted rows from Credentials.csv for quick reference."""
    df = load_credentials_df()
    sample = df.head(limit)[["ID", "NAME", "EMAIL", "PASSWORD", "CARD_NO"]].copy()
    return sample


def is_authenticated() -> bool:
    """Check if the current session is authenticated."""
    if st is None:
        return False
    return st.session_state.get("logged_in", False) and st.session_state.get("user") is not None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get active user metadata from session state."""
    if st is None:
        return None
    return st.session_state.get("user")


def login_user(user_data: Dict[str, Any]) -> None:
    """Store authenticated user in session state."""
    if st is not None:
        st.session_state["logged_in"] = True
        st.session_state["user"] = user_data


def logout_user() -> None:
    """Clear session state and log out."""
    if st is not None:
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state.clear()
        st.rerun()
