"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from ai_validation.models import Model
from ai_validation.utils import get_actual_experiment, get_application


class Matrix:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Confusion Matrix page", page_icon="⚖", layout="wide")
        _, col, _ = st.columns([2, 3, 2])
        with col:
            st.title("⚖ Confusion Matrix")
        self.app = get_application()

    def select_model(self, model_list: list[Model]) -> Optional[list[Model]]:
        selected_model_list: list[Model] = []
        selected_name = st.multiselect(
            "Select here all the models for which you want to see the confusion matrix",
            [i.model_name for i in model_list],
        )
        if not selected_name:
            return None
        for model in model_list:
            if model.model_name in selected_name:
                selected_model_list.append(model)
        return selected_model_list

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
            st.warning("There is no run done for this experiment")
            return
        list_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id)
        if list_ais is None:
            st.warning("No run done for this experiment")
            return
        if "true_positives" not in list_ais[0].metrics:
            st.warning("This is not a binary comparison experiment, it's not possible to show a confusion matrix.")
            return
        col1, _, col2 = st.columns([2, 1, 8])
        with col1:
            selected_models = self.select_model(list_ais)
            if selected_models is None:
                return
        with col2:
            for model in selected_models:
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.subheader(" ")
                    st.subheader(" ")
                    st.subheader(" ")
                    st.subheader(model.model_name)
                    st.subheader("Metrics : ", help=model.get_metrics_expaliner([], True))
                    st.subheader("Hyperparameters : ", help=model.get_param_explainer())
                with col_b:
                    matrix = [
                        [model.metrics["true_positives"], model.metrics["false_positives"]],
                        [model.metrics["false_negatives"], model.metrics["true_negatives"]],
                    ]
                    fig, _ = plt.subplots()
                    sns.heatmap(matrix, annot=True, cmap="Reds")
                    st.pyplot(fig)
        _, col, _ = st.columns([1, 2, 1])


if __name__ == "__main__":
    ui = Matrix()
    ui.render()
