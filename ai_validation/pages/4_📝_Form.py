"""
File used to show a already completed Form
(just like in the history (with admin view) of the ai_sustainability Form)
"""

import streamlit as st

from ai_sustainability.package_business.models import Username
from ai_sustainability.package_user_interface.pages_elements.form_element import (
    FormRender,
)
from ai_sustainability.package_user_interface.utils_streamlit import (
    get_application as get_application_form,
)
from ai_validation.utils import get_application


class Form:
    """Class used to show a Form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Form page", page_icon="📝")
        st.title("📝 Form")
        self.app = get_application()
        self.app_form = get_application_form()
        self.form_ui = FormRender(Username(""), self.app_form)

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        selected_experiment = (
            st.session_state.selected_experiment if "selected_experiment" in st.session_state else None
        )
        if selected_experiment is None:
            st.warning("No experiment selected, please select one")
            return
        st.caption(
            f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
        )

        username, _, form_name = self.app.get_form_id(selected_experiment.experiment_id).split("-")

        # get the list with all previous answers contained in the form
        previous_form_answers = self.app_form.get_previous_form(Username(username), form_name)
        self.form_ui.render_as_text(previous_form_answers)

        list_bests_ais = self.app_form.get_best_ais(Username(username), form_name)
        self.form_ui.show_best_ai(list_bests_ais)

        if previous_form_answers.experiment_id is not None:
            st.caption(
                f"The mlflow's experiment id corresponding to this form is : {previous_form_answers.experiment_id}"
            )
        else:
            st.warning("There is no mlflow experiment for this form.")


if __name__ == "__main__":
    ui = Form()
    ui.render()
