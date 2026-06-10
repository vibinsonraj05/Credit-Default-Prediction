import streamlit as st
from login import show_login
from dashboard import show_dashboard

st.set_page_config(
    page_title="Credit Card Risk Dashboard",
    page_icon="💳",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["logged_in"]:
    show_dashboard()
else:
    show_login()