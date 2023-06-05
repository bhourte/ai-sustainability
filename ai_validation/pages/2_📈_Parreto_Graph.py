"""File used to show the result of the tests made by the expert in mlflow"""

import math
from typing import Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_validation.models import Model
from ai_validation.utils import get_actual_experiment, get_application


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
        dataframe_infos = pd.DataFrame(data=dico)
        fig = px.scatter(
            dataframe_infos,
            x=metric1,
            y=metric2,
            color="Is Optimal ?",
            hover_name="Model name",
            color_discrete_sequence=["red" if i else "grey" for _, i in list_pareto_point],
        )
        st.plotly_chart(fig)

    def show_ranked_model(self, list_pareto_score: list[Tuple[Model, float, bool]], metric1: str, metric2: str) -> None:
        """Method used to show all model in a ranked order for the 2 selected metrics"""
        col1, col2 = st.columns([5, 4])
        with col2:
            st.caption(" ")
            show_all_models = st.checkbox("Show all model?", help="Check if you want to see all models")
        with col1:
            help_text = f"The score corresponds to the distance between the point and the origin of the graph.  \n A point in the upper right corner will have 100% while a point in the 2 extreme corners will have a score of {round(1/math.sqrt(2), 2)}%"
            number_of_models = (
                len(list_pareto_score) if show_all_models else [i for _, _, i in list_pareto_score].count(True)
            )
            st.subheader(
                f"There are {number_of_models} {'optimal' if not show_all_models else ''} models :",
                help=help_text,
            )
        i = 1
        for model, score, is_pareto in list_pareto_score:
            if is_pareto or show_all_models:
                col1, col2 = st.columns([1, 6])
                with col1:
                    st.subheader(f"{i})")
                with col2:
                    help_text = f"Metrics :  \n{model.get_metrics_expaliner([metric1, metric2])}  \n  \n  \nHyperparameters :  \n{model.get_param_explainer()}"
                    st.subheader(model.model_name, help=help_text)
                    st.caption(
                        f"Score : {round(score*100, 2)}%{    'This model is optimal' if is_pareto and show_all_models else ''}"
                    )
                i += 1

    def rank_and_show_models(self, list_pareto_point: list[Tuple[Model, bool]], metric1: str, metric2: str) -> None:
        """Method used to sort the list of model and show them as a ranked list"""
        list_pareto_score: list[Tuple[Model, float, bool]] = []
        for model, is_pareto in list_pareto_point:
            score = math.sqrt(
                model.normalized_metrics[metric1] ** 2 + model.normalized_metrics[metric2] ** 2
            ) / math.sqrt(2)
            list_pareto_score.append((model, score, is_pareto))
        list_pareto_score.sort(key=lambda x: x[1], reverse=True)
        self.show_ranked_model(list_pareto_score, metric1, metric2)

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        selected_experiment = get_actual_experiment()
        if selected_experiment is None:
            return

        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        if form_id is None:
            st.warning("There is no filled form for this experiment, but runs were found.")

        col1, col2 = st.columns([10, 5])
        with col2:
            st.caption(" ")
            st.caption(" ")  # To align
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

        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        self.app.set_normalized_metrics(list_ais, selected_metrics)

        list_pareto_point = self.app.get_pareto_points(list_ais, selected_metrics[0], selected_metrics[1])
        self.plot_comparison_graph(list_pareto_point, selected_metrics[0], selected_metrics[1])
        self.rank_and_show_models(list_pareto_point, selected_metrics[0], selected_metrics[1])


if __name__ == "__main__":
    ui = Parreto()
    ui.render()
