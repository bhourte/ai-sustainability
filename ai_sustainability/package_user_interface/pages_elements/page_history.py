"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form
"""
import streamlit as st
from decouple import config

from ai_sustainability.package_business.models import Username
from ai_sustainability.package_user_interface.pages_elements.form_element import (
    FormRender,
)
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
    get_application,
)


class HistoricStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_choice_user : show a select box with all users
        - show_choice_form : show a select box with all forms of a user
        - show_submission_button : display a button where the user can save the changes made in the form
        - show_best_ai : show the n best AIs
        - render_as_user : show a editable Form already completed
        - render_as_admin : show a previous answered Form with the admin view
    """

    def __init__(self) -> None:
        self.app = get_application()
        self.username = check_user_connection()
        self.form_ui = FormRender(self.username, self.app)
        st.session_state.clicked = False

    def show_choice_user(self, list_username: list[Username]) -> Username:
        """
        Show a select box with all users
        """
        list_username = [Username("<Select a user>")] + list_username
        question = "Select an user"
        answer = Username(str(st.selectbox(label=question, options=list_username, index=0)))
        return answer if answer != "<Select a user>" else Username("")

    def show_choice_form(self, list_answered_form_name: list[str]) -> str:
        """
        Show a select box with all forms of a user
        """
        list_form_name = ["<Select a form>"] + list_answered_form_name
        question = (
            "Select a form"
            if self.username == config("ADMIN_USERNAME")
            else "Select the previous form you want to see again or edit"
        )
        selected_form_name = str(st.selectbox(label=question, options=list_form_name, index=0))
        return selected_form_name if selected_form_name != "<Select a form>" else ""

    def show_submission_button(self) -> bool:
        """
        Display a button where the user can save the changes made in the form
        """
        if st.button("Save changes"):
            st.write("Changes saved")
            st.session_state.last_form_name = None
            return True
        return False

    def render_as_user(self, username: Username) -> None:
        """
        Function used to select and show a form with the User view
        """
        list_answered_form = self.app.get_all_forms_names(username)
        selected_form = self.show_choice_form(list_answered_form)
        if not selected_form:  # if none form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        form = self.app.get_previous_form(username, selected_form)

        new_form, new_form_name = self.form_ui.render(form)
        if new_form is None:
            return

        list_bests_ais = self.app.calcul_best_ais(new_form)
        self.form_ui.show_best_ai(list_bests_ais)
        self.form_ui.show_best_ai_graph(list_bests_ais)
        if self.show_submission_button():
            self.app.save_answers(new_form, list_bests_ais, new_form_name)

    def render_as_admin(self) -> None:
        """
        Function used to select and show a form with the Admin view
        """
        list_username = self.app.get_all_users()

        # The admin select an user
        choosen_user = self.show_choice_user(list_username)
        if not choosen_user:  # if no user selected, don't show the rest
            return

        # The admin select a form of the choosen user
        list_answered_form = self.app.get_all_forms_names(choosen_user)
        selected_form_name = self.show_choice_form(list_answered_form)
        if not selected_form_name:  # if no form selected, don't show the rest
            return

        # get the list with all previous answers contained in the form
        previous_form_answers = self.app.get_previous_form(choosen_user, selected_form_name)
        self.form_ui.render_as_text(previous_form_answers)

        list_bests_ais = self.app.get_best_ais(choosen_user, selected_form_name)
        self.form_ui.show_best_ai(list_bests_ais)

    def render(self) -> None:
        # Connected as an Admin
        if self.username == config("ADMIN_USERNAME"):
            self.render_as_admin()
        # Connected as an User
        else:
            self.render_as_user(self.username)
