"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form
"""
import streamlit as st

from ai_sustainability.classes.class_form import FormStreamlit
from ai_sustainability.utils.utils_streamlit import check_user_connection


class HistoricStreamlit(FormStreamlit):
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - set_atribute : set the page attributes
        - show_choice_user : show a select box with all users
        - show_choice_form : show a select box with all forms of a user
        - show_submission : show a previous answered form
        - show_question_as_admin : show a previous answered form with the admin view
    """

    page_title = "Historic Page"
    form_title = "Historic"
    page_icon = "📜"

    def __init__(self) -> None:
        super().__init__()

    def show_choice_user(self, list_username: list[str]) -> str:
        list_username = ["<Select a user>"] + list_username
        question = "Select an user"
        answer = str(st.selectbox(label=question, options=list_username, index=0))
        return answer if answer != "<Select a user>" else ""

    def show_choice_form(self, list_answered_form: list[str], is_admin: bool = False) -> str:
        list_form_name = ["<Select a form>"]
        for elmt_i in list_answered_form:
            list_form_name.append(elmt_i.rsplit("-", maxsplit=1)[-1])
        question = "Select a form" if is_admin else "Select the previous form you want to see again or edit"
        answer = str(st.selectbox(label=question, options=list_form_name, index=0))
        if answer == "<Select a form>":
            # we put that here, so it's executed only one time and the form is not blocked by the session_state
            st.session_state.clicked = False
            return ""
        index_sol = list_form_name.index(answer) - 1
        return list_answered_form[index_sol]

    def show_submission_button(self) -> bool:
        if st.button("Save changes", disabled=st.session_state.clicked):
            st.write("Changes saved")
            st.session_state.last_form_name = None
            return True
        return False

    def show_question_as_admin(self, dict_question: dict, previous_answers: list[str]) -> None:
        if dict_question["question_label"] == "end":
            return
        question = dict_question["question_text"]
        answers = ""
        for previous_answer in previous_answers:
            answers += f"{previous_answer} <br>"
        st.subheader(f"{question} :")
        st.caption(answers, unsafe_allow_html=True)
