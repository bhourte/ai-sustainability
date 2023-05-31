"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_validation.global_variables import METRIC_IMPLEMENTED
from ai_validation.models import Experiment, Model
from ai_validation.utils import get_application


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Experiment selection page", page_icon="🔍")
        st.title("🔍 Experiment selection")
        self.app = get_application()

    def select_user(self, list_username: list[str]) -> Optional[str]:
        """Method used to show all user and select one"""
        list_username = ["<Select a user>", "<All user>"] + list_username
        question = "Select an user"
        selected_user = str(st.selectbox(label=question, options=list_username, index=0))
        if selected_user == "<All user>":
            return None
        return selected_user if selected_user != "<Select a user>" else ""

    def select_experiment(self, list_experiment: list[Experiment]) -> Optional[Experiment]:
        """Method used to show all not empty experiment and used to select one"""
        list_exp = [f"{i.experiment_name} with id : {i.experiment_id}" for i in list_experiment]
        list_exp = ["<Select a experiment>"] + list_exp
        question = "Select a experiment by is name"
        selected_experiment = str(st.selectbox(label=question, options=list_exp, index=0))
        return (
            list_experiment[list_exp.index(selected_experiment) - 1]
            if selected_experiment != "<Select a experiment>"
            else None
        )

    def plot_comparison_graph(self, list_model: list[Model], list_metrics: list[str]) -> None:
        """Method used to show a big graph with 2 axes and show Pareto Front"""
        # TODO faire en sorte de pouvoir choisir ses metrics
        print(list_metrics)
        selected_metrics = st.multiselect("Select 2 metrics to compare models :", list_metrics, max_selections=2)
        if len(selected_metrics) < 2:
            return
        metric1 = selected_metrics[0]
        metric2 = selected_metrics[1]
        dico: dict = {}
        list_pareto_point = self.app.get_pareto_points(list_model, metric1, metric2)
        dico[metric1] = [i.normalized_metrics[metric1] for i, _ in list_pareto_point]
        dico[metric2] = [i.normalized_metrics[metric2] for i, _ in list_pareto_point]
        dico["Is Optimal ?"] = ["Yes" if i else "No" for _, i in list_pareto_point]
        dico["Model name"] = [i.model_name for i, _ in list_pareto_point]
        df = pd.DataFrame(data=dico)
        fig = px.scatter(df, x=metric1, y=metric2, color="Is Optimal ?", hover_data="Model name")
        st.plotly_chart(fig)

    def plot_small_graph(self, model: Model, selected_metric: str) -> None:
        """Method used to show a litle bar graph for a model"""
        # TODO ameliorer ca, ca ne ressemble visuellement a rien :
        # *) scale entre 0 et 100 (certain a 50 prennent tout l'espace)
        # *) taille de graph
        # *) mettre en couleur la selected_metric
        hover_text = [repr(metric) for metric in model.normalized_metrics]  # text with the in and out node
        values = [model.normalized_metrics[metric] * 100 for metric in model.normalized_metrics]
        list_metric_name = list(model.normalized_metrics)  # To get the edges name in ascending order
        fig = go.Figure(data=[go.Bar(x=list_metric_name, y=values, dy=100)])
        fig.update_layout(
            yaxis={
                "dtick": 1,
            },
        )
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True, height=200)

    def show_ordered_ais(self, list_of_ai: list[Model], selected_metric: str) -> None:
        """
        Method used to show an ordered list of ais

        parameters:
            - list_of_ai: list of tuple as : (ai_name, ai_score, str of parametrers, str of metrics)
            in which the 1st ai has the best score and so on
        """
        for i, model in enumerate(list_of_ai):
            col1, col2, col3 = st.columns([1, 15, 15])
            with col1:
                st.caption(body=f"{i+1})")
            with col2:
                st.caption(body=model.model_name, help=model.get_param_explainer())
            with col3:
                st.caption(
                    body=f"score : {round(model.normalized_metrics[selected_metric]*100, 1)}%",
                    help=model.get_metrics_expaliner(METRIC_IMPLEMENTED, get_all_metrics=True),
                )
                # self.plot_small_graph(model, selected_metric)

    def show_calculation_global_score(self, list_metrics: list[str]) -> None:
        """Method used to show how the score is calculated from each metrics"""
        # TODO changer l'affichage de global score pour qu'il soit correct 1/max_error par ex
        text = " * ".join(list_metrics)
        st.subheader(
            body=f"How Global Score is obtained : \n {text}",
            help="Each metrcis is normalized between 0 and 1 before being put in the calculation",
        )

    def show_best_ai_graph(self, list_of_ais: list[Model], selected_metric) -> None:
        if list_of_ais:
            labels = [i.model_name for i in list_of_ais]
            values = [i.normalized_metrics[selected_metric] for i in list_of_ais]
            fig = go.Figure(
                data=[
                    go.Pie(labels=labels, values=values, hovertemplate="%{label}<br>Score: %{value:.2f}<extra></extra>")
                ]
            )
            st.plotly_chart(fig)

    def select_ranking(self, list_metrics: list[str]) -> str:
        """Used to show a select box where the user can choose how to rank the Ais"""
        choice = ["Global score"] + list_metrics
        return str(st.selectbox(label="Rank AIs by : ", options=choice, index=0))

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        list_user = self.app.get_all_user()
        selected_user = self.select_user(list_user)
        if not selected_user and selected_user is not None:
            return

        list_experiments = self.app.get_experiment_from_user(selected_user)
        if list_experiments is None:
            st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
            return
        if not list_experiments:
            st.warning("There is no experiment for this user")
            return
        selected_experiment = self.select_experiment(list_experiments)
        if selected_experiment is None:
            return
        st.session_state.selected_experiment = selected_experiment

        st.caption(
            f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
        )


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
