"""File used to show the result of the tests made by the expert in mlflow"""

import plotly.graph_objects as go
import streamlit as st

from ai_validation.application import Application
from ai_validation.models import Model

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


class Ranking:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Ranking", page_icon="🥇")
        st.title("🥇 Ranking")
        self.app = get_application()

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
                    help=model.get_metrics_expaliner(METRIC_USED, get_all_metrics=True),
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

        selected_experiment = (
            st.session_state.selected_experiment if "selected_experiment" in st.session_state else None
        )
        if selected_experiment is None:
            st.warning("No experiment selected, please select one")
            return
        st.caption(
            f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
        )

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
        self.show_best_ai_graph(list_ais, selected_metric)


if __name__ == "__main__":
    ui = Ranking()
    ui.render()
