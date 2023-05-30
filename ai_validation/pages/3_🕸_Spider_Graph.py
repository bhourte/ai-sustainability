"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
        col1, col2 = st.columns([1, 4])
        with col1:
            selected_metrics = self.select_metrics(list_metrics)
            selected_models = self.select_model(list_ais)
            if selected_models is None:
                return
            self.app.set_normalized_metrics(list_ais, selected_metrics)
        with col2:
            for model in selected_models:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader(model.model_name)
                    st.subheader("All metrics : ", help=model.get_metrics_expaliner(selected_metrics, True))
                    st.subheader(
                        "Normalized metrics : ",
                        help=model.get_metrics_expaliner(selected_metrics, True, normalized=True),
                    )
                    st.subheader("Hyperparameters : ", help=model.get_param_explainer())
                with col_b:
                    values = [model.normalized_metrics[i] for i in selected_metrics]
                    df = pd.DataFrame(dict(value=values, variable=selected_metrics))
                    fig = px.line_polar(df, r="value", theta="variable", line_close=True, text="value")
                    fig.update_traces(fill="toself", textposition="top center")
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
                    st.plotly_chart(fig)


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
