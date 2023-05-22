"""
Class which contains the form composed of the different questions/answers
Streamlit class
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
            st.session_state.last_form_name = None
            return True
        return False

    def render(self) -> None:
        form, form_name = self.form_ui.render()
        if form is None:
            return
        form.form_name = form_name
        form.username = self.username

        list_bests_ais = self.app.calcul_best_ais(form)
        if self.show_submission_button():  # show the submission button and return True if it's clicked
            self.form_ui.show_best_ai(list_bests_ais)
            self.form_ui.show_best_ai_graph(list_bests_ais)

            with st.spinner("Saving..."):
                experiment_id = self.app.create_experiment(self.username, form_name)
                if experiment_id is not None:
                    st.caption(f"The mlflow's experiment id corresponding to this form is : {experiment_id}")
                else:
                    st.warning("A problem occurred while creating the mlflow experiment. ")
                self.app.save_answers(form, list_bests_ais, experiment_id)
                st.write("Answers saved")
