"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form

methods:
    - display_historic_of_all_users (Admin only)
    - display_historic_of_one_user 
    - get_list_results
    - ...
"""
import streamlit as st

from ai_sustainability.classes.utils_streamlit import check_user_connected


class HistoricStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
    """

    def __init__(self, database_link) -> None:
        self.database_link = database_link

        st.set_page_config(page_title="Historic Page", page_icon="📜")
        st.title("📜Historic")
        self.username = check_user_connected()
