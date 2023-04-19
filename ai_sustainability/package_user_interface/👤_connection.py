"""
This file is the main file
launch it with: streamlit run 👤_connection.py
"""
import streamlit as st
from ai_sustainability.package_user_interface.pages_elements.page_connection import (
    ConnectionStreamlit,
)


def main() -> None:
    """
    This is the code used to show the "Connection" page
    The user will connect here and be able to acces to the rest of the application after that
    """

    st.set_page_config(page_title="Connection Page", page_icon="👤")
    st.title("👤Connection")
    st_connect = ConnectionStreamlit()
    st_connect.setup_username()


if __name__ == "__main__":
    main()
