"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import streamlit as st
from decouple import config

from ai_validation.models import Experiment
from ai_validation.utils import get_application


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Experiment selection page", page_icon="🔍")
        st.title("🔍 Experiment selection")
        self.app = get_application()

    def select_user(self, list_username: list[str]) -> Optional[str]:
        """Method used to show all user and select one"""
        list_username = ["<Select an user>", "<All experiments>", "<Only independant experiments>"] + list_username
        question = "Select an user"
        selected_user = str(st.selectbox(label=question, options=list_username, index=0))
        if selected_user == "<All experiments>":
            return None
        return selected_user if selected_user != "<Select an user>" else ""

    def select_experiment(self, list_experiment: list[Experiment]) -> Optional[Experiment]:
        """Method used to show all not empty experiment and used to select one"""
        list_exp = [f"{i.experiment_name} with id : {i.experiment_id}" for i in list_experiment]
        list_exp = ["<Select an experiment>"] + list_exp
        question = "Select an experiment by is name"
        selected_experiment = str(st.selectbox(label=question, options=list_exp, index=0))
        return (
            list_experiment[list_exp.index(selected_experiment) - 1]
            if selected_experiment != "<Select an experiment>"
            else None
        )

    def render(self) -> None:
        """
        This is the code used to render the form and used by the user to fill it
        """

        list_user = self.app.get_all_user()
        selected_user = self.select_user(list_user)
        if not selected_user and selected_user is not None:
            return

        list_experiments: list[Experiment] = []
        if selected_user == "<Only independant experiments>":
            all_experiments = self.app.get_experiment_from_user(None)
            if all_experiments is None:
                st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
                return
            experiments_id_with_form: list[str] = []
            for user in list_user:
                experiments_of_user = self.app.get_experiment_from_user(user)
                if experiments_of_user is None:
                    st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
                    return
                experiments_id_with_form += [exp.experiment_id for exp in experiments_of_user]
            for experiment in all_experiments:
                if experiment.experiment_id not in experiments_id_with_form:
                    list_experiments.append(experiment)
        else:
            list_experiments_bis = self.app.get_experiment_from_user(selected_user)
            if list_experiments_bis is None:
                st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
                return
            if not list_experiments_bis:
                st.warning("There is no experiment for this user")
                return
            list_experiments = list_experiments_bis
        selected_experiment = self.select_experiment(list_experiments)
        if selected_experiment is None:
            return
        st.session_state.selected_experiment = selected_experiment

        st.caption(
            f"Experiment selected : {selected_experiment.experiment_name} with id : {selected_experiment.experiment_id}"
        )


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
