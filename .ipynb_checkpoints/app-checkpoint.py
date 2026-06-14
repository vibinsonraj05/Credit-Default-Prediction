import streamlit as st
from login import show_login
from dashboard import show_dashboard

# MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="Credit Card Risk Dashboard",
    page_icon="💳",
    layout="wide"
)

# ===== SESSION STATE INIT =====
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

# ===== ROUTING =====
if st.session_state["logged_in"]:
    show_dashboard()
else:
    show_login()