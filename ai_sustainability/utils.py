"""Utils functions for the Streamlit app."""
import streamlit as st


def check_username() -> str:
    if "username" not in st.session_state or st.session_state.username == "":
        # User not connected, don't show the form, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return ""
    return st.session_state.username
