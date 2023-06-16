"""
This file is used to show the Historic page
"""
import streamlit as st

from ai_sustainability.package_user_interface.pages_elements.page_history import (
    HistoricStreamlit,
)


def main() -> None:
    """
    This is the code used to show the previous form completed by an User
    Different usage if User or Admin
    """
    st.set_page_config(page_title="History Page", page_icon="📜")
    st.title("📜History")
    st_historic = HistoricStreamlit()

    username = st_historic.username
    if not username:
        return

    st_historic.render()


if __name__ == "__main__":
    main()
