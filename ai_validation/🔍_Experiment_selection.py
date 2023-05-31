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
        list_username = ["<Select a user>", "<All user>"] + list_username
        question = "Select an user"
        selected_user = str(st.selectbox(label=question, options=list_username, index=0))
        if selected_user == "<All user>":
            return None
        return selected_user if selected_user != "<Select a user>" else ""

    def select_experiment(self, list_experiment: list[Experiment]) -> Optional[Experiment]:
        """Method used to show all not empty experiment and used to select one"""
        list_exp = [f"{i.experiment_name} with id : {i.experiment_id}" for i in list_experiment]
        list_exp = ["<Select a experiment>"] + list_exp
        question = "Select a experiment by is name"
        selected_experiment = str(st.selectbox(label=question, options=list_exp, index=0))
        return (
            list_experiment[list_exp.index(selected_experiment) - 1]
            if selected_experiment != "<Select a experiment>"
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

        list_experiments = self.app.get_experiment_from_user(selected_user)
        if list_experiments is None:
            st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
            return
        if not list_experiments:
            st.warning("There is no experiment for this user")
            return
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
