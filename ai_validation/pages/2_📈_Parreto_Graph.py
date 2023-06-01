"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_validation.models import Experiment, Model
from ai_validation.utils import get_application


class Parreto:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Pareto graph", page_icon="📈")
        st.title("📈 Pareto graph")
        self.app = get_application()

    def plot_comparison_graph(self, list_pareto_point: list[Tuple[Model, bool]], metric1: str, metric2: str) -> None:
        """Method used to show a big graph with 2 axes and show Pareto Front"""
        dico: dict = {}
        dico[metric1] = [i.normalized_metrics[metric1] for i, _ in list_pareto_point]
        dico[metric2] = [i.normalized_metrics[metric2] for i, _ in list_pareto_point]
        dico["Is Optimal ?"] = ["Yes" if i else "No" for _, i in list_pareto_point]
        dico["Model name"] = [i.model_name for i, _ in list_pareto_point]
        df = pd.DataFrame(data=dico)
        fig = px.scatter(df, x=metric1, y=metric2, color="Is Optimal ?", hover_data="Model name")
        st.plotly_chart(fig)

    def show_pareto_point(self, list_pareto_point: list[Tuple[Model, bool]], metric1: str, metric2: str) -> None:
        """Method used to show all parreto point for the 2 metrics selected"""
        st.subheader(f"There are {[i for _, i in list_pareto_point].count(True)} optimal models :")
        for model, is_parreto in list_pareto_point:
            if is_parreto:
                help_text = f"Metrics :  \n{model.get_metrics_expaliner([metric1, metric2])}  \n  \n  \nHyperparameters :  \n{model.get_param_explainer()}"
                st.subheader(model.model_name, help=help_text)

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        selected_experiment: Experiment = (
            st.session_state.selected_experiment if "selected_experiment" in st.session_state else None
        )
        if selected_experiment is None:
            st.warning("No experiment selected, please select one")
            return
        st.caption(
            f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
        )

        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        if form_id is None:
            st.warning("There is no filled form for this experiment, but runs were found.")

        col1, col2 = st.columns([10, 5])
        with col2:
            st.caption(" ")
            st.caption(" ")
            help_text = (
                "If not checked, displays only the metrics provided from the completed form"
                if form_id is not None
                else "There is no completed form for this experiment, so all metrics are allowed."
            )
            all_metric: bool = st.checkbox("Allow all metrics?", help=help_text, disabled=(form_id is None))
        with col1:
            if all_metric or form_id is None:
                list_metrics = self.app.get_all_metrics(selected_experiment.experiment_id)
                if list_metrics is None:
                    st.warning("No run logs for this experiment")
                    return
            else:
                list_metrics = self.app.get_metrics(form_id)
            selected_metrics = st.multiselect("Select 2 metrics to compare models :", list_metrics, max_selections=2)
            if len(selected_metrics) < 2:
                return

        print(list_metrics)

        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        # ranked_ais = list[Tuple(Model, dict[metric: normalized_metric])]
        self.app.set_normalized_metrics(list_ais, selected_metrics)

        list_pareto_point = self.app.get_pareto_points(list_ais, selected_metrics[0], selected_metrics[1])
        self.plot_comparison_graph(list_pareto_point, selected_metrics[0], selected_metrics[1])
        self.show_pareto_point(list_pareto_point, selected_metrics[0], selected_metrics[1])


if __name__ == "__main__":
    ui = Parreto()
    ui.render()
