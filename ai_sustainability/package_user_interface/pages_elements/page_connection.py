"""
Class for connection page,
Streamlit class
"""
import streamlit as st
from decouple import config

from ai_sustainability.package_business.models import Username
from ai_sustainability.utils import check_if_name_ok


class ConnectionStreamlit:
    """
    Class used to show all the streamlit UI for the connection page

    Methods :
        - __init__
        - setup_username : setup the username for all pages
    """

    _username: Username = Username("")

    def __init__(self) -> None:
        st.set_page_config(page_title="Connection Page", page_icon="👤")
        st.title("👤Connection")

    def setup_username(self) -> None:
        username = Username(
            st.text_input(
                "Put your username here to connect :",
                st.session_state.username if "username" in st.session_state else "",
            )
        )

        if not username:  # User connected
            st.caption("❌Not connected")
            return

        dash, elmt = check_if_name_ok(username)
        if dash:
            st.warning(f"You can't use {elmt} in your username")
            return

        st.caption(
            f"🔑Connected as an {username}" if username == config("ADMIN_USERNAME") else f"✅Connected as {username}"
        )
        st.session_state.username = self._username = username
        # To detect if the user create a form with the same name as the previous one (used in Historic)
        st.session_state.last_form_name = None
        st.session_state.clicked = False
        return
