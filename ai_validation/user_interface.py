"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_validation.application import Application
from ai_validation.models import Experiment, Model

METRIC_USED = [
    "Duration",
    "false_negatives",
    "false_positives",
    "max_error",
    "mean_absolute_error",
    "f1_score_handmade",
    "f1_score",
    "evaluation_accuracy",
]


# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Result page", page_icon="🔍")
        st.title("🔍 Result")
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
        # TODO rendre ca + joli (noms axes, changer "color", ajout nom model surtout mdr, etc.)
        print(list_metrics)
        metric1 = list_metrics[0]
        metric2 = list_metrics[1]
        list_pareto_point = self.app.get_pareto_points(list_model, metric1, metric2)
        metric1_values = [i.normalized_metrics[metric1] for i, _ in list_pareto_point]
        metric2_values = [i.normalized_metrics[metric2] for i, _ in list_pareto_point]
        text_parreto = [i for _, i in list_pareto_point]
        fig = px.scatter(x=metric1_values, y=metric2_values, color=text_parreto)
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
                    help=model.get_metrics_expaliner(METRIC_USED, get_all_metrics=False),
                )
                # self.plot_small_graph(model, selected_metric)

    def show_calculation_global_score(self, list_metrics: list[str]) -> None:
        """Method used to show how the score is calculated from each metrics"""
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
        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        list_metrics = self.app.get_metrics(form_id)

        selected_metric = self.select_ranking(list_metrics)
        print(list_metrics)

        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        # ranked_ais = list[Tuple(Model, dict[metric: normalized_metric])]
        self.app.set_normalized_metrics(list_ais, list_metrics)
        list_ais.sort(key=lambda x: x.normalized_metrics[selected_metric], reverse=True)
        self.show_ordered_ais(list_ais, selected_metric)
        if selected_metric == "Global score":
            self.show_calculation_global_score(list_metrics)
        # self.show_best_ai_graph(list_ais, selected_metric)
        self.plot_comparison_graph(list_ais, list_metrics)


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
