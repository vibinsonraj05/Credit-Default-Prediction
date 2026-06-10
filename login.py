import streamlit as st
import pandas as pd


def show_login():

    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%)
        }

        h1 {
            text-align: center;
            color: black;
        }
    </style>
    """, unsafe_allow_html=True)

    users = pd.read_csv(
        "Dataset/Credentials.csv",
        dtype={"CARD_NO": str, "ACCOUNT_NO": str}
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1>🔐 Login</h1>", unsafe_allow_html=True)

        email = st.text_input("Email ID", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):

            user = users[
                (users["EMAIL"] == email) &
                (users["PASSWORD"] == password)
            ]

            if user.empty:
                st.error("❌ Invalid credentials")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user"] = user.iloc[0].to_dict()

                st.success("✅ Login successful!")
                st.rerun()