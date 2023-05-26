"""File used to show the result of the tests made by the expert in mlflow"""

from typing import Optional

import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_validation.application import Application
from ai_validation.models import Experiment


# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        st.set_page_config(page_title="Result page", page_icon="🔍")
        st.title("🔍 Result")
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

    def show_ordered_ais(self, list_of_ai: list[tuple[str, float, str, str]]) -> None:
        """
        Method used to show an ordered list of ais

        parameters:
            - list_of_ai: list of tuple as : (ai_name, ai_score, str of parametrers, str of metrics)
            in which the 1st ai has the best score and so on
        """
        for i, (ai_name, ai_score, params, metrics) in enumerate(list_of_ai):
            col1, col2, col3 = st.columns([1, 15, 15])
            with col1:
                st.caption(body=f"{i+1})")
            with col2:
                st.caption(body=ai_name, help=params)
            with col3:
                st.caption(body=f"score : {ai_score}", help=metrics)

    def show_calculation(self, list_metrics: list[str]) -> None:
        """Method used to show how the score is calculated from each metrics"""
        text = " * ".join(list_metrics)
        st.subheader(
            body=f"How score is obtained : \n {text}",
            help="Each metrcis is normalized between 0 and 1 before being put in the calculation",
        )

    def show_best_ai_graph(self, list_of_ais: list[tuple[str, float, str, str]]) -> None:
        if list_of_ais:
            labels = [i[0] for i in list_of_ais]
            values = [i[1] for i in list_of_ais]
            fig = go.Figure(
                data=[
                    go.Pie(labels=labels, values=values, hovertemplate="%{label}<br>Score: %{value:.2f}<extra></extra>")
                ]
            )
            st.plotly_chart(fig)

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
        form_id = self.app.get_form_id(selected_experiment.experiment_id)
        list_metrics = self.app.get_metrics(form_id)
        print(list_metrics)

        ranked_ais = self.app.get_ai_from_experiment(selected_experiment.experiment_id, list_metrics)
        if ranked_ais is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        self.show_ordered_ais(ranked_ais)
        self.show_calculation(list_metrics)
        self.show_best_ai_graph(ranked_ais)


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
