"""File used to show the result of the tests made by the expert in mlflow"""

import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_sustainability.package_business.models import Username
from ai_validation.application import Application


# @st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


class UserInterface:
    """Class used to show all result of experiment based on the form"""

    def __init__(self) -> None:
        self.app = get_application()

    def select_user(self, list_username: list[Username]) -> Username:
        """Method used to show all user and used to select one"""
        list_username = [Username("<Select a user>"), Username("<All user>")] + list_username
        question = "Select an user"
        selected_user = Username(str(st.selectbox(label=question, options=list_username, index=0)))
        return selected_user if selected_user != "<Select a user>" else Username("")

    def select_experiment(self, list_exp_name: list[str], list_exp_ids: list[str]) -> str:
        """Method used to show all not empty experiment and used to select one"""
        list_exp = [f"{val_i} with id : {list_exp_ids[i]}" for i, val_i in enumerate(list_exp_name)]
        list_exp = ["<Select a experiment>"] + list_exp
        question = "Select a experiment by is name"
        selected_experiment = str(st.selectbox(label=question, options=list_exp, index=0))
        return (
            list_exp_ids[list_exp.index(selected_experiment) - 1]
            if selected_experiment != "<Select a experiment>"
            else ""
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

    def show_best_ai_graph(self, list_of_ais: list[tuple[str, float]]) -> None:
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
        st.set_page_config(page_title="Result page", page_icon="🔍")
        st.title("🔍 Result")

        list_user = self.app.get_all_user()
        selected_user = self.select_user(list_user)
        if not selected_user:
            return
        all_user = selected_user == "<All user>"

        exp = self.app.get_experiment_from_user(selected_user, all_user)
        if exp is None:
            st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
            return
        list_experiments, list_ids = exp
        if not list_experiments:
            st.warning("There is no experiment for this user")
            return
        selected_experiment = self.select_experiment(list_experiments, list_ids)
        if not selected_experiment:
            return

        val = self.app.get_ai_from_experiment(selected_experiment)
        if val is None:
            st.warning("There is no runs done for this experiment, or no correct runs.")
            return
        ranked_ais, list_metrics = val
        self.show_ordered_ais(ranked_ais)
        self.show_calculation(list_metrics)
        self.show_best_ai_graph(ranked_ais)


if __name__ == "__main__":
    ui = UserInterface()
    ui.render()
