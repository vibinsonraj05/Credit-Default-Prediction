import streamlit as st
import pandas as pd

def show_login():

    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    # ===== BACKGROUND ONLY =====
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(90deg,rgba(42, 123, 155, 1) 0%, rgba(87, 199, 133, 1) 50%, rgba(237, 221, 83, 1) 100%);
        }

        /* STOP INPUT EXPANDING */
        div[data-baseweb="input"] {
            width: 100% !important;
        }

        /* REMOVE FOCUS ZOOM SHIFT */
        input {
            box-sizing: border-box;
        }

        /* CENTER TITLE */
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

    # ===== CENTER WRAPPER =====
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown("<h1>🔐 Login</h1>", unsafe_allow_html=True)

        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            user = users[
                (users["EMAIL"] == email) &
                (users["PASSWORD"] == password)
            ]

            if user.empty:
                st.error("Invalid credentials")
            else:
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.user = user.iloc[0]
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)