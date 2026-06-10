import streamlit as st
import pandas as pd

def show_login():

    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(
                90deg,
                rgba(42,123,155,1) 0%,
                rgba(87,199,133,1) 50%,
                rgba(237,221,83,1) 100%
            );
        }

        div[data-baseweb="input"] {
            width: 100% !important;
        }

        input {
            box-sizing: border-box;
        }

        h1 {
            text-align: center;
            color: black;
        }
    </style>
    """, unsafe_allow_html=True)

    users = pd.read_csv(
        "Dataset/Credentials.csv",
        dtype={
            "CARD_NO": str,
            "ACCOUNT_NO": str
        }
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown("<h1>🔐 Login</h1>", unsafe_allow_html=True)

        email = st.text_input(
            "Email ID",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            width="stretch",
            key="login_btn"
        ):

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