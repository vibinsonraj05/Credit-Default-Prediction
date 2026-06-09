import streamlit as st
from login import show_login
from dashboard import show_dashboard

st.set_page_config(
    page_title="Credit Card Risk Dashboard",
    page_icon="💳",
    layout="wide"
)

# Session state init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Routing
if not st.session_state.logged_in:
    show_login()
else:
    show_dashboard()