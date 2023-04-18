"""
ONLY STREAMLIT UTILS, who puts DB connect here died

function usefull for the project's UI

method:
    - check_user_connection
    - dash_error : show the error message if no_dash_in_my_text retrun True
"""
import streamlit as st
from decouple import config

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import Username
from ai_sustainability.package_data_access.db_connection import DbConnection


@st.cache_resource
def get_application() -> Application:
    database = DbConnection()
    app = Application(database)
    return app


def check_user_connection() -> Username:
    if "username" not in st.session_state or st.session_state.username == "":
        # User not connected, don't show the form, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return Username("")
    username = st.session_state.username
    # Connected as an Admin
    if username == config("ADMIN_USERNAME"):
        st.caption("🔑 Connected as an Admin")
    # Connected as an User
    else:
        st.caption("✅ Connected as " + str(username))
    # To detect if the user create a form with the same name as the previous one (used in Historic)
    return st.session_state.username


def dash_error() -> None:
    st.warning("Please don't use dash in your form name")
