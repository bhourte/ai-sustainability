"""
Class for connection page,
Streamlit class
"""
import streamlit as st

from ai_sustainability.classes.utils import no_dash_in_my_text


class ConnectionStreamlit:
    """
    Class used to show all the streamlit UI for the connection page

    Methods :
        - __init__
        - setup_username : setup the username for all pages
    """

    _username: str = ""

    def __init__(self) -> None:
        st.set_page_config(page_title="Connection Page", page_icon="👤")
        st.title("👤Connection")

    def setup_username(self) -> None:  # TODO remove return
        username = st.text_input(
            "Put your username here to connect :",
            st.session_state.username if "username" in st.session_state else "",
        )

        if not username:  # User connected
            st.caption("❌Not connected")
            return

        dash, elmt = no_dash_in_my_text(
            username
        )  # TODO name of function changed by verbs and split in 2 functions (username, text_input)
        if dash:
            st.warning(f"You can't use {elmt} in your username")
            return

        st.caption(f"🔑Connected as an {username}" if username == "Admin" else f"✅Connected as {username}")
        st.session_state.username = self._username = username
        # To detect if the user create a form with the same name as the previous one (used in Historic)
        st.session_state.last_form_name = None
        st.session_state.clicked = False
        return
