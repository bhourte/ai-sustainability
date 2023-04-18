"""
Class which contains the hisoric of the different questions/answers of the users
Streamlit class
inherit from class_form
"""
import streamlit as st

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import Username
from ai_sustainability.package_user_interface.pages_elements.form_element import (
    FormRender,
)
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
)


class HistoricStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_choice_user : show a select box with all users
        - show_choice_form : show a select box with all forms of a user
        - show_submission_button : display a button where the user can save the changes made in the form
        - show_question_as_admin : show a previous answered question with the admin view
    """

    def __init__(self, app: Application) -> None:
        self.app = app
        self.username = check_user_connection()
        self.form_ui = FormRender(self.username, app)

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

    def show_submission_button(self) -> bool:
        """
        Display a button where the user can save the changes made in the form
        """
        if st.button("Save changes"):
            st.write("Changes saved")
            st.session_state.last_form_name = None
            return True
        return False

    def show_best_ai(self, list_bests_ais: list[str]) -> None:
        """
            Method used to show the n best AI obtained after the user has completed the Form
            The number of AI choosen is based on the nbai wanted by the user and
            the maximum of available AI for the use of the user
            (If there is only 3 AI possible, but the user asked for 5, only 3 will be shown)

        Parameters:
            - list_bests_ais (list): list of the n best AI
        """
        if not list_bests_ais:  # If no AI corresponding the the choices
            st.subheader(
                "There is no AI corresponding to your request, please make other choices in the form", anchor=None
            )
            return

        st.subheader(
            f"There is {len(list_bests_ais)} IA corresponding to your specifications, here they are in order of the most efficient to the least:",
            anchor=None,
        )
        for index, best_ai in enumerate(list_bests_ais):
            st.caption(f"{index + 1}) {best_ai}")

    def render_as_user(self, username: Username) -> None:
        """
        Function used to show a form with the User view
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
        self.show_best_ai(list_bests_ais)
        print(new_form.question_list)
        if self.show_submission_button():
            self.app.save_answers(new_form, list_bests_ais, new_form_name)

    def render_as_admin(self) -> None:
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
        self.form_ui.render_as_text(previous_form_answers)

        list_bests_ais = self.app.get_best_ais(choosen_user, selected_form_name)
        self.show_best_ai(list_bests_ais)
