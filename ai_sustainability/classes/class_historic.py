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

    def show_choice_user(self, list_username: list[str]) -> str:
        list_username = ["<Select a user>"] + list_username
        question = "Select an user"
        answer = str(st.selectbox(label=question, options=list_username, index=0))
        if answer == "<Select a user>":
            return ""
        return answer

    def show_choice_form(self, list_answered_form, admin: bool = False) -> str:
        list_form_name = ["<Select a form>"] + list_answered_form
        question = "Select the previous form you want to see again or edit"
        if admin:
            question = "Select a form"
        answer = str(st.selectbox(label=question, options=list_form_name, index=0))
        if answer == "<Select a form>":
            # we put that here, so it's executed only one time and the form is not blocked
            st.session_state.clicked = False
            return ""
        return answer

    def show_submission(self, answers: list[list[str]]) -> bool:
        if st.button("Change answer", disabled=st.session_state.clicked):
            st.write("Answers saved")
            st.write(answers)
            st.session_state.last_form_name = None
            return True
        return False

    def show_question_as_admin(self, dict_question: dict, previous_answers: list[str]) -> None:
        if dict_question["question_label"] == "end":
            return
        question = dict_question["question_text"]
        answers = ""
        for i in previous_answers:
            answers += i + "<br>"
        st.subheader(question + " :")
        st.caption(answers, unsafe_allow_html=True)
