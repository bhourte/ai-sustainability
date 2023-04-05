"""
Class for statistic page
Streamlit class

methods:
    - __init__
    - display_statistic_edges
    - display_statistic_ais
"""
import streamlit as st

from ai_sustainability.classes.utils_streamlit import check_user_connection


class StatisticStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
    """

    def __init__(self, database_link) -> None:
        self.database_link = database_link

        st.set_page_config(page_title="Statistic Page", page_icon="📊")
        st.title("📊Statistic")
        self.username = check_user_connection()
