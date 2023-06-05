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
from ai_validation.global_variables import DENOMINATOR_METRICS, NUMERATOR_METRICS
from ai_validation.utils import get_actual_experiment, get_application


class Form:
    """Class used to show a Form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Form page", page_icon="📝")
        st.title("📝 Form")
        self.app = get_application()
        self.app_form = get_application_form()
        self.form_ui = FormRender(Username(""), self.app_form)

    def show_calculation_global_score(self, list_metrics: list[str]) -> None:
        """Method used to show how the score is calculated from each metrics in a latex syntax"""
        list_numerator: list[str] = []
        list_denominator: list[str] = []
        for metric in list_metrics:
            if metric in NUMERATOR_METRICS:
                list_numerator.append(metric)
            if metric in DENOMINATOR_METRICS:
                list_denominator.append(metric)

        if not list_numerator:
            list_numerator.append("1")
        numerator = "*".join(list_numerator).replace("_", "\\;")
        denominator = "*".join(list_denominator).replace("_", "\\;")
        latex_text = "Global\\;Score\\;=\\;"
        if not list_denominator:
            latex_text += numerator
        else:
            latex_text += "\\frac{" + numerator + "}{" + denominator + "}"
        st.header(
            body="There is a way to obtain a Global Score :",
            help="The metrics used to calculate the Global Score are those that correspond to the choices made by the user in the form he has completed just here above.",
        )
        st.latex(
            latex_text,
            help="The global score need to be normalized between 0 and 1 after the calculation (1 for the best and 0 for the worst) in order to have a meaning.",
        )

    def show_relevant_metrics(self, form_id: str) -> None:
        """Method used to show the relevant metrics thanks to the answers given by the user in the Form"""
        list_metrics = self.app.get_metrics(form_id)
        st.header(" ")
        st.header("And here are the metrics corresponding to the User's choice :")
        for metric in list_metrics:
            st.subheader(metric)
        self.show_calculation_global_score(list_metrics)

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        selected_experiment = get_actual_experiment()
        if selected_experiment is None:
            return

        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        if form_id is None:
            st.warning("There is no filled form for this experiment, so nothing to show.")
            return
        username, _, form_name = form_id.split("-")

        # get the list with all previous answers contained in the form
        previous_form_answers = self.app_form.get_previous_form(Username(username), form_name)
        self.form_ui.render_as_text(previous_form_answers)

        list_bests_ais = self.app_form.get_best_ais(Username(username), form_name)
        self.form_ui.show_best_ai(list_bests_ais)

        self.show_relevant_metrics(form_id)


if __name__ == "__main__":
    ui = Form()
    ui.render()
