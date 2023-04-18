"""
This file is used to show the Statistic page
"""
import streamlit as st

from ai_sustainability.package_user_interface.pages_elements.page_statistic import (
    StatisticPage,
)
from ai_sustainability.package_user_interface.utils_streamlit import get_application


def main() -> None:
    """
    This is the code used by the admin to see statistics from the answers of the users
    """

    st.set_page_config(page_title="Statistic Page", page_icon="📊")
    # Connection to the online gremlin database via db_connection.py
    app = get_application()
    st_statistic = StatisticPage(app)
    username = st_statistic.username
    if not username:
        return
    st_statistic.render()


if __name__ == "__main__":
    main()
