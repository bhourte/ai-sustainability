"""
Class for connection page,
Streamlit class

methods:
    
"""
import streamlit as st


class ConnectionStreamlit:
    """
    Class used to show all the streamlit UI for the connection page

    Methods :
        - setup_username : setup the username for all pages
    """

    def __init__(self) -> None:
        st.set_page_config(page_title="Connection Page", page_icon="👤")
        st.title("👤Connection")
        self.username = ""
        st.session_state.clicked = False

    def setup_username(self) -> str:
        username = st.text_input(
            "Put your username here to connect :",
            st.session_state.username if "username" in st.session_state else "",
        )

        if not username:  # User connected
            st.caption("❌Not connected")
            return ""

        if "-" in username:
            st.warning("You can't use '-' in your username")
            return ""

        st.caption(f"🔑Connected as an {username}" if username == "Admin" else f"✅Connected as {username}")
        st.session_state.username = username
        # To detect if the user create a form with the same name as the previous one (used in Historic)
        st.session_state.last_form_name = None
        st.session_state.clicked = False
        self.username = username
        return username
