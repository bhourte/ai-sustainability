# TODO put it all in class_form and use it from class_form

"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form
"""
import streamlit as st

from ai_sustainability.package_business.models import Form, Username
from ai_sustainability.package_user_interface.classes.page_form import FormStreamlit


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

    def show_form_as_text(self, form: Form) -> None:
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

    def historic_user(self, username: Username) -> None:
        """
        Function used to show a form with the User view
        """
        list_answered_form = self.app.get_all_forms_names(username)
        selected_form = self.show_choice_form(list_answered_form)
        if not selected_form:  # if none form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        form = self.app.get_previous_form(username, selected_form)
        # TODO change all the "answer", previous_answers, etc names to clarify this all

        form, is_ended = self.get_all_questions_and_answers(form)
        if not is_ended:
            return

        # We ask the user to give us a name for the form (potentially a new one)
        new_form_name, form_name_incorrect = self.input_form_name_and_check(form.form_name)
        if form_name_incorrect:
            return

        # If the name is already taken by an other form
        if self.app.check_form_exist(username, new_form_name) and new_form_name != form.form_name:
            if self.check_name_already_taken(username):
                return

        list_bests_ais = self.app.calcul_best_ais(form)
        self.show_best_ai(list_bests_ais)
        if self.show_submission_button():
            self.app.change_answers(
                form, new_form_name, list_bests_ais
            )  # TODO change name to save_answer and change the function in DbConnection

    def historic_admin(self) -> None:
        """
        Function used to show a form with the Admin view
        """
        list_username = self.app.get_all_users()

        # The admin select an user
        choosen_user = self.show_choice_user(list_username)
        if not choosen_user:  # if no user selected, don't show the rest
            return

        # The admin select a form of the choosen user
        list_answered_form = self.app.get_all_forms_names(choosen_user)
        selected_form_name = self.show_choice_form(list_answered_form, is_admin=True)
        if not selected_form_name:  # if no form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        previous_form_answers = self.app.get_previous_form(choosen_user, selected_form_name)
        self.show_form_as_text(previous_form_answers)

        list_bests_ais = self.app.get_best_ais(choosen_user, selected_form_name)
        self.show_best_ai(list_bests_ais)
