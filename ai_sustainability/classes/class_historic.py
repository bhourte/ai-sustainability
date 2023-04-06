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

from ai_sustainability.classes.class_form import FormStreamlit
from ai_sustainability.classes.utils_streamlit import check_user_connection


class HistoricStreamlit(FormStreamlit):
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
    """

    def __init__(self, database_link) -> None:
        super().__init__(database_link, False)
        self.set_atribute()

    def set_atribute(self) -> None:
        st.set_page_config(page_title="Historic Page", page_icon="📜")
        st.title("📜Historic")
        self.username = check_user_connection()

    def show_choice_form(self, list_answered_form) -> str:
        list_form_name = ["<Select a form>"] + list_answered_form
        return ""
