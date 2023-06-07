"""File used to show the result of the tests made by the expert in mlflow"""

import os
from typing import Optional

import streamlit as st

from ai_validation.models import Model
from ai_validation.utils import get_actual_experiment, get_application


class Artifacts:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Artifacts page", page_icon="👁")
        _, col, _ = st.columns([2, 3, 2])
        with col:
            st.title("👁 Artifacts")
        self.app = get_application()

    def select_model(self, model_list: list[Model]) -> Optional[Model]:
        """Method used to show all not empty experiment and used to select one"""
        name_list = ["<Select a Model>"] + [i.model_name for i in model_list]
        question = "Select a Model"
        selected_experiment = str(st.selectbox(label=question, options=name_list, index=0))
        return (
            model_list[name_list.index(selected_experiment) - 1] if selected_experiment != "<Select a Model>" else None
        )

    def render(self) -> None:
        """
        This is the code used to render the page with all loged artifact
        """
        selected_experiment = get_actual_experiment()
        if selected_experiment is None:
            return

        list_models = self.app.get_model_from_experiment(selected_experiment.experiment_id)
        if list_models is None:
            st.warning("No run done for this experiment")
            return
        selected_models = self.select_model(list_models)
        if selected_models is None:
            return
        path = self.app.get_artifact_path(selected_experiment, selected_models)
        if path is None:
            st.warning("There is no artifact for this model")
            return
        for file in os.listdir(path):
            print(file)
            if file[len(file) - 4 : len(file)] == ".png":
                st.subheader(file[: len(file) - 4])
                st.image(path + "/" + file)


if __name__ == "__main__":
    ui = Artifacts()
    ui.render()
