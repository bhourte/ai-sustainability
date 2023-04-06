"""
ONLY STREAMLIT UTILS, who puts DB connect here died

function usefull for the project's UI

method:
    - check_user_connection
    - dash_error : show the error message if no_dash_in_my_text retrun True
"""
import streamlit as st


def check_user_connection() -> str:
    if "username" not in st.session_state or st.session_state.username == "":
        # User not connected, don't show the form, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return ""
    username = st.session_state.username
    # Connected as an User
    if username != "Admin":
        st.caption("✅ Connected as " + str(username))
    # Connected as an Admin
    else:
        st.caption("🔑 Connected as an Admin")
    # To detect if the user create a form with the same name as the previous one (used in Historic)
    return st.session_state.username


def dash_error() -> None:
    st.warning("Please don't use dash in your form name")
