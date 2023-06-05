"""File used to show the result of the tests made by the expert in mlflow"""

import plotly.graph_objects as go
import streamlit as st

from ai_validation.global_variables import DENOMINATOR_METRICS, NUMERATOR_METRICS
from ai_validation.models import Model
from ai_validation.utils import get_actual_experiment, get_application


class Ranking:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Ranking page", page_icon="🥇", layout="wide")
        _, col, _ = st.columns([2, 3, 2])
        with col:
            st.title("🥇 Ranking")
        self.app = get_application()

    def plot_small_graph(self, model: Model, selected_metric: str) -> None:
        """Method used to show a litle bar graph for a model"""
        list_metric_name = list(model.normalized_metrics)
        values = [model.normalized_metrics[metric] * 100 for metric in list_metric_name]
        selected = ["blue"] * len(list_metric_name)
        selected[list_metric_name.index(selected_metric)] = "green"

        fig = go.Figure(data=[go.Bar(x=list_metric_name, y=values, marker_color=selected)])
        fig.update_yaxes(nticks=2, range=[0, 100])
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
            col1, col2, col3 = st.columns([1, 10, 20])
            with col1:
                st.subheader(" ")
                st.subheader(" ")  # To align with the graph
                st.subheader(" ")
                st.subheader(body=f"{i+1})")
            with col2:
                st.subheader(" ")
                st.subheader(" ")  # To align with the graph
                st.subheader(" ")
                st.subheader(
                    body=model.model_name,
                    help=model.get_param_explainer() + "  \n  \n" + model.get_metrics_expaliner([], True),
                )
            with col3:
                self.plot_small_graph(model, selected_metric)

    def show_calculation_global_score(self, list_metrics: list[str]) -> None:
        """Method used to show how the global score is calculated from each metrics (in a latex syntax)"""
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

        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.subheader(
                body="How Global Score is obtained :",
                help="The metrics used to calculate the Global Score are those that correspond to the choices made by the user in the form he has completed.",
            )
            st.latex(
                latex_text,
                help="The global score is normalized between 0 and 1 after the calculation (1 for the best and 0 for the worst)",
            )

    def show_best_ai_graph(self, list_of_ais: list[Model], selected_metric) -> None:
        """Method used to show a pie shart with all runs"""
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

        _, col, _ = st.columns([2, 3, 2])
        with col:
            selected_experiment = get_actual_experiment()
            if selected_experiment is None:
                return

            list_metrics = self.app.get_all_metrics(selected_experiment.experiment_id)
            if list_metrics is None:
                st.warning("There is no run done for the selected experiment")
                return

        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        if form_id is None:
            st.warning("There is no filled form for this experiment, but runs were found.")
        form_list_metrics = self.app.get_metrics(form_id) if form_id is not None else list_metrics

        selected_metric = self.select_ranking(list_metrics)
        if selected_metric == "Global score":
            self.show_calculation_global_score(form_list_metrics)

        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        self.app.set_normalized_metrics(list_ais, list_metrics, form_list_metrics)
        list_ais.sort(key=lambda x: x.normalized_metrics[selected_metric], reverse=True)
        self.show_ordered_ais(list_ais, selected_metric)

        _, col, _ = st.columns([1, 4, 2])
        with col:
            self.show_best_ai_graph(list_ais, selected_metric)


if __name__ == "__main__":
    ui = Ranking()
    ui.render()
