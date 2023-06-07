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

    def render_dual(self, list_models: list[Model], selected_experiment: Experiment) -> None:
        col1, _, col2 = st.columns([5, 1, 5])
        cols = [col1, col2]
        selected_models = []
        for col in cols:
            with col:
                selected_models.append(self.select_model(list_models, str(col)))
        if selected_models[0] is None or selected_models[1] is None:
            return

        paths = []
        dict_artifacts_name = {}
        possible_col = [True, True]
        lists_artifacts: list[list[str]] = [[], []]
        for i, col in enumerate(cols):
            with col:
                paths.append(self.app.get_artifact_path(selected_experiment, selected_models[i]))
                if paths[0] is None:
                    st.warning("There is no artifact for this model")
                    possible_col[i] = False
                nb_artifacts = 0
                for file in os.listdir(paths[i]):
                    if file[len(file) - 4 : len(file)] == ".png":
                        dict_artifacts_name[file] = True
                        lists_artifacts[i].append((file))
                        nb_artifacts += 1
                if nb_artifacts == 0:
                    st.warning("There is no artifact for this model")
                    possible_col[i] = False

        for artifact in dict_artifacts_name:
            container = st.container()
            with container:
                colc, _, colv = st.columns([5, 1, 5])
                cola = [colc, colv]
                for i, col in enumerate(cola):
                    if possible_col[i]:
                        with col:
                            st.subheader(" ")
                            st.subheader(f"{artifact[: len(artifact) - 4].replace('_', ' ')}:")
                            if artifact in lists_artifacts[i]:
                                st.image(f"{paths[i]}/{artifact}")
                            else:
                                st.warning(
                                    f'"{artifact[: len(artifact) - 4].replace("_", " ")}" is not available for this model'
                                )

        return

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
        return (
            self.render_dual(list_models, selected_experiment)
            if two_mode
            else self.render_mono(list_models, selected_experiment)
        )


if __name__ == "__main__":
    ui = Artifacts()
    ui.render()
