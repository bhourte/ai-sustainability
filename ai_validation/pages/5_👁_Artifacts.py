"""File used to show the result of the tests made by the expert in mlflow"""

import os
from typing import Optional

import streamlit as st

from ai_validation.models import Experiment, Model
from ai_validation.utils import get_actual_experiment, get_application


class Artifacts:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Artifacts page", page_icon="👁", layout="wide")
        _, col, _ = st.columns([2, 3, 2])
        with col:
            st.title("👁 Artifacts")
        self.app = get_application()

    def select_model(self, model_list: list[Model], key: str) -> Optional[Model]:
        """Method used to show all not empty experiment and used to select one"""
        name_list = ["<Select a Model>"] + [i.model_name for i in model_list]
        question = "Select a Model"
        selected_experiment = str(st.selectbox(label=question, options=name_list, index=0, key=key))
        return (
            model_list[name_list.index(selected_experiment) - 1] if selected_experiment != "<Select a Model>" else None
        )

    def render_mono(self, list_models: list[Model], selected_experiment: Experiment) -> None:
        _, col, _ = st.columns([2, 3, 2])
        with col:
            selected_models = self.select_model(list_models, "")
            if selected_models is None:
                return

            path = self.app.get_artifact_path(selected_experiment, selected_models)
            if path is None:
                st.warning("There is no artifact for this model")
                return

            nb_artifacts = 0
            for file in os.listdir(path):
                if file[len(file) - 4 : len(file)] == ".png":
                    st.subheader(" ")
                    st.subheader(f"{file[: len(file) - 4].replace('_', ' ')}:")
                    st.image(path + "/" + file)
                    nb_artifacts += 1
            if nb_artifacts == 0:
                st.warning("There is no artifact for this model")
                return

    def select_two_models(self, list_models: list[Model]) -> Optional[list]:
        col1, _, col2 = st.columns([5, 1, 5])
        cols = [col1, col2]
        selected_models = []
        for col in cols:
            with col:
                selected_models.append(self.select_model(list_models, str(col)))
        if selected_models[0] is None or selected_models[1] is None:
            return None
        return selected_models

    def get_and_show_all_artifacts_dual(self, selected_models: list[Model], selected_experiment: Experiment) -> None:
        col1, _, col2 = st.columns([5, 1, 5])
        cols = [col1, col2]
        paths = []
        dict_artifacts_name = {}
        lists_artifacts: list[list[str]] = [[], []]

        for i, col in enumerate(cols):
            with col:
                paths.append(self.app.get_artifact_path(selected_experiment, selected_models[i]))
                if paths[i] is None:
                    st.warning("There is no corresponding artifact directory for this model")
                else:
                    nb_artifacts = 0
                    for file in os.listdir(paths[i]):
                        if file[len(file) - 4 : len(file)] == ".png":
                            dict_artifacts_name[file] = True
                            lists_artifacts[i].append((file))
                            nb_artifacts += 1
                    if nb_artifacts == 0:
                        st.warning("There is no logged artifact for this model")
        self.show_all_artifacts_dual(dict_artifacts_name, lists_artifacts, paths)

    def show_all_artifacts_dual(
        self,
        dict_artifacts_name: dict,
        lists_artifacts: list[list[str]],
        paths: list[Optional[str]],
    ) -> None:
        for artifact in dict_artifacts_name:
            with st.container():
                col1, _, col2 = st.columns([5, 1, 5])
                cols = [col1, col2]
                for i, col in enumerate(cols):
                    if len(lists_artifacts[i]) > 0:
                        with col:
                            name = artifact[: len(artifact) - 4].replace("_", " ")
                            st.subheader(" ")
                            st.subheader(f"{name}:")
                            if artifact in lists_artifacts[i]:
                                st.image(f"{paths[i]}/{artifact}")
                            else:
                                st.warning(f'"{name}" is not available for this model')

    def render_dual(self, list_models: list[Model], selected_experiment: Experiment) -> None:
        selected_models = self.select_two_models(list_models)
        if selected_models is None:
            return

        self.get_and_show_all_artifacts_dual(selected_models, selected_experiment)

    def render(self) -> None:
        """
        This is the code used to render the page with all loged artifact
        """
        _, col, _ = st.columns([2, 3, 2])
        with col:
            selected_experiment = get_actual_experiment()
            if selected_experiment is None:
                return

            list_models = self.app.get_model_from_experiment(selected_experiment.experiment_id)
            if list_models is None:
                st.warning("No run done for this experiment")
                return

            two_mode = st.checkbox("Compare 2 models?", help="Check if you want to compare 2 model side-by-side.")
        if two_mode:
            self.render_dual(list_models, selected_experiment)
        else:
            self.render_mono(list_models, selected_experiment)


if __name__ == "__main__":
    ui = Artifacts()
    ui.render()
