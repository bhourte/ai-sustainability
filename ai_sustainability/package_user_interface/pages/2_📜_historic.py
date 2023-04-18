"""
This file is used to show the Historic page
"""
import streamlit as st

from ai_sustainability.package_user_interface.classes.page_historic import (
    HistoricStreamlit,
)
from ai_sustainability.package_user_interface.utils_streamlit import get_application

ADMIN_USERNAME = "Admin"  # TODO .env


def main() -> None:
    """
    This is the code used to show the previous form completed by an User
    Different usage if User or Admin
    """
    st.set_page_config(page_title="Historic Page", page_icon="📜")
    st.title("📜Historic")
    # TODO create a render function
    app = get_application()
    st_historic = HistoricStreamlit(app)
    username = st_historic.username
    if not username:
        return

    # Connected as an User
    if username != ADMIN_USERNAME:
        st_historic.historic_user(username)
    # Connected as an Admin
    else:
        st_historic.historic_admin()


if __name__ == "__main__":
    main()
