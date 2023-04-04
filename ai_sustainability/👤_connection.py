"""
This file is the main file
launch it with: streamlit run 👤_connection.py
"""
import streamlit as st


def setup_username() -> None:
    username = st.text_input(
        "Put your username here to connect :",
        st.session_state.username if "username" in st.session_state else "",
    )

    if not username:  # User connected
        st.caption("❌Not connected")
        return

    if "-" in username:
        st.warning("You can't use '-' in your username")
        return

    st.caption(f"🔑Connected as an {username}" if username == "Admin" else f"✅Connected as {username}")
    st.session_state.username = username
    st.session_state.last_form_name = None  # To detect if the user create a form with the same name as the previous one
    st.session_state.clicked = False


def main() -> None:
    """
    This is the code used to show the "Connection" page
    The user will connect here and be able to acces to the rest of the application after that
    """

    st.set_page_config(page_title="Connection Page", page_icon="👤")
    st.title("👤Connection")
    setup_username()


if __name__ == "__main__":
    main()
