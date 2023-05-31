"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ai_validation.models import Experiment, Model
from ai_validation.utils import get_application


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Spider Graph page", page_icon="🕸", layout="wide")
        st.title("🕸 Spider Graph")
        self.app = get_application()

    def select_model(self, model_list: list[Model]) -> Optional[list[Model]]:
        selected_model_list: list[Model] = []
        selected_name = st.multiselect(
            "select here all the models you want to display in a spider graph", [i.model_name for i in model_list]
        )
        if not selected_name:
            return None
        for model in model_list:
            if model.model_name in selected_name:
                selected_model_list.append(model)
        return selected_model_list

    def select_metrics(self, metric_list: list[str]) -> list[str]:
        return st.multiselect("Select all metrics you want to analyse", metric_list)

    def show_comparison_plot(self, model_list: list[Model], metric_list: list[str]) -> None:
        selected_models_name = st.multiselect(
            "Select 2 models to compare :", [i.model_name for i in model_list], max_selections=2
        )
        if len(selected_models_name) < 2:
            return
        selected_models: list[Model] = []
        for model in model_list:
            if model.model_name in selected_models_name:
                selected_models.append(model)
        fig = go.Figure()
        metric1 = [selected_models[0].normalized_metrics[metric] for metric in metric_list]
        fig.add_trace(go.Scatterpolar(r=metric1, theta=metric_list, fill="toself", name=selected_models[0].model_name))
        metric2 = [selected_models[1].normalized_metrics[metric] for metric in metric_list]
        fig.add_trace(go.Scatterpolar(r=metric2, theta=metric_list, fill="toself", name=selected_models[1].model_name))
        fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 1]}}, showlegend=False)
        st.plotly_chart(fig)

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
        list_metrics = self.app.get_all_metrics(selected_experiment.experiment_id)
        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("No run done for this experiment")
            return
        col1, _, col2 = st.columns([1, 1, 4])
        with col1:
            selected_metrics = self.select_metrics(list_metrics)
            selected_models = self.select_model(list_ais)
            if selected_models is None:
                return
            self.app.set_normalized_metrics(list_ais, selected_metrics)
        with col2:
            for model in selected_models:
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.subheader(" ")
                    st.subheader(" ")
                    st.subheader(" ")
                    st.subheader(model.model_name)
                    st.subheader("All metrics : ", help=model.get_metrics_expaliner(selected_metrics, True))
                    st.subheader(
                        "Normalized metrics : ",
                        help=model.get_metrics_expaliner(selected_metrics, normalized=True),
                    )
                    st.subheader("Hyperparameters : ", help=model.get_param_explainer())
                with col_b:
                    values = [model.normalized_metrics[i] for i in selected_metrics]
                    df = pd.DataFrame({"value": values, "variable": selected_metrics})
                    fig = px.line_polar(df, r="value", theta="variable", line_close=True, text="value")
                    fig.update_traces(fill="toself", textposition="top center")
                    fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 1]}})
                    st.plotly_chart(fig)
        self.show_comparison_plot(selected_models, selected_metrics)


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
