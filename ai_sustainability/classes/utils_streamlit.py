"""
ONLY STREAMLIT UTILS, who puts DB connect here died

function usefull for the project's UI

method:
    - check_user_connection
    - ...
"""
import streamlit as st


def check_user_connected() -> str:
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
    st.session_state.last_form_name = None
    st.session_state.clicked = False
    return st.session_state.username
