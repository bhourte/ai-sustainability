"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
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

    def show_confusion_matrix(self, model: Model) -> None:
        matrix = [
            [model.metrics["true_positives"], model.metrics["false_negatives"]],
            [model.metrics["false_positives"], model.metrics["true_negatives"]],
        ]
        annot = np.asarray(
            [f"TP\n{matrix[0][0]}", f"FN\n{matrix[0][1]}", f"FP\n{matrix[1][0]}", f"TN\n{matrix[1][1]}"]
        ).reshape((2, 2))
        fig, _ = plt.subplots()
        hm = sns.heatmap(matrix, annot=annot, fmt="", cmap="Reds")
        hm.set_xlabel("Predicted label")
        hm.xaxis.set_ticklabels(["Positive", "Negative"])
        hm.set_ylabel("True label")
        hm.yaxis.set_ticklabels(["Positive", "Negative"])
        st.pyplot(fig)

    def show_other_metrics(self, model: Model) -> None:
        tp = model.metrics["true_positives"]
        tn = model.metrics["true_negatives"]
        fp = model.metrics["false_positives"]
        fn = model.metrics["false_negatives"]
        st.subheader(f"Precision = {tp/(tp+fp)}", help="= PPV = TP/(TP+FP)")
        st.subheader(f"Recall = {tp/(tp+fn)}", help="= TPR = TP/(TP+FN)")
        st.subheader(f"Sensitivity = {tp/(tp+fn)}", help="= TPR = TP/(TP+FN)  \n= Recall")
        st.subheader(f"Specificity = {tn/(tn+fp)}", help="= TNR = TN/(TN+FP)")
        phi = (tp * tn - fp * fn) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        st.subheader(
            f"phi = {phi}",
            help="= MCC = (TP * TN-FP * FN)/sqrt((TP+FP) * (TP+FN) * (TN+FP) * (TN+FN))  \n(= Matthews correlation coefficient)",
        )

    def render(self) -> None:
        """
        This is the code used to render the page with all the confusion matrix
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
        list_ais = self.app.get_model_from_experiment(selected_experiment.experiment_id)
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
                    st.subheader(
                        model.model_name,
                        help=model.get_param_explainer() + "  \n  \n" + model.get_metrics_expaliner([], True),
                    )
                    st.subheader(" ")
                    self.show_other_metrics(model)
                with col_b:
                    self.show_confusion_matrix(model)
                st.subheader(" ")
        _, col, _ = st.columns([1, 2, 1])


if __name__ == "__main__":
    ui = Matrix()
    ui.render()
