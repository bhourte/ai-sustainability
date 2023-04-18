# TODO put it all in class_form and use it from class_form

"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form
"""
import streamlit as st

from ai_sustainability.package_business.models import (
    AnswersList,
    Form,
    Question,
    Username,
)
from ai_sustainability.package_user_interface.classes.class_form import FormStreamlit


class HistoricStreamlit(FormStreamlit):
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_choice_user : show a select box with all users
        - show_choice_form : show a select box with all forms of a user
        - show_submission_button : display a button where the user can save the changes made in the form
        - show_question_as_admin : show a previous answered question with the admin view
    """

    page_title = "Historic Page"
    form_title = "Historic"
    page_icon = "📜"

    def show_choice_user(self, list_username: list[Username]) -> Username:
        """
        Show a select box with all users
        """
        list_username = [Username("<Select a user>")] + list_username
        question = "Select an user"
        answer = Username(str(st.selectbox(label=question, options=list_username, index=0)))
        return answer if answer != "<Select a user>" else Username("")

    def show_choice_form(self, list_answered_form: list[str], is_admin: bool = False) -> str:
        """
        Show a select box with all forms of a user
        """
        list_form_name = ["<Select a form>"] + list_answered_form
        question = "Select a form" if is_admin else "Select the previous form you want to see again or edit"
        answer = str(st.selectbox(label=question, options=list_form_name, index=0))
        if answer == "<Select a form>":
            # we put that here, so it's executed only one time and the form is not blocked by the session_state
            st.session_state.clicked = False
            return ""
        return answer

    def show_submission_button(self) -> bool:  # TODO use it from the calass_form
        """
        Display a button where the user can save the changes made in the form
        """
        if st.button("Save changes"):
            st.write("Changes saved")
            st.session_state.last_form_name = None
            return True
        return False

    def show_form_as_admin(self, form: Form) -> None:
        """
        Show a previous answered question with the admin view
        """
        actual_question = 0
        while form.question_list[actual_question].type != "end":
            answers = ""
            for previous_answer in form.question_list[actual_question].answers_choosen:
                answers += f"{previous_answer.text} <br>"
            st.subheader(f"{form.question_list[actual_question].text} :")
            st.caption(answers, unsafe_allow_html=True)
            actual_question += 1
