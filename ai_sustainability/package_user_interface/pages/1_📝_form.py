"""
This file is used to show the From page
"""
import streamlit as st

from ai_sustainability.package_user_interface.pages_elements.form_element import (
    FormRender,
)
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
    get_application,
)


class FormStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_submission_button
        - set_locked : lock all the question of the form
        - show_best_ai
        - render
    """

    def __init__(self) -> None:
        self.app = get_application()
        self.username = check_user_connection()
        self.form_ui = FormRender(self.username, self.app)

    def set_locked(self) -> None:
        self.form_ui.locked = True

    def show_submission_button(self) -> bool:
        if st.button("Submit", on_click=self.set_locked, disabled=self.form_ui.locked):
            st.write("Answers saved")
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

    def render(self) -> None:
        form, form_name = self.form_ui.render()
        if form is None:
            return
        form.form_name = form_name
        form.username = self.username

        list_bests_ais = self.app.calcul_best_ais(form)
        if self.show_submission_button():  # show the submission button and return True if it's clicked
            self.show_best_ai(list_bests_ais)
            self.app.save_answers(form, list_bests_ais)


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    st.set_page_config(page_title="Form Page", page_icon="📝")
    st.title("📝Form")

    st_form = FormStreamlit()
    username = st_form.username
    if not username:
        return
    st_form.render()


if __name__ == "__main__":
    main()
