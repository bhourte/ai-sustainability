"""File used to show the result of the tests made by the expert in mlflow"""

import plotly.graph_objects as go
import streamlit as st
from decouple import config

from ai_sustainability.package_business.models import Username
from ai_validation.application import Application


@st.cache_resource
def get_application() -> Application:
    app = Application()
    return app


def select_user(list_username: list[Username]) -> Username:
    """Method used to show all user and used to select one"""
    list_username = [Username("<Select a user>"), Username("<All user>")] + list_username
    question = "Select an user"
    selected_user = Username(str(st.selectbox(label=question, options=list_username, index=0)))
    return selected_user if selected_user != "<Select a user>" else Username("")


def select_experiment(list_exp_name: list[str], list_exp_ids: list[str]) -> str:
    """Method used to show all not empty experiment and used to select one"""
    list_exp = [f"{val_i} with id : {list_exp_ids[i]}" for i, val_i in enumerate(list_exp_name)]
    list_exp = ["<Select a experiment>"] + list_exp
    question = "Select a experiment by is name"
    selected_experiment = str(st.selectbox(label=question, options=list_exp, index=0))
    return (
        list_exp_ids[list_exp.index(selected_experiment) - 1] if selected_experiment != "<Select a experiment>" else ""
    )


def show_ordered_ais(list_of_ai: list[tuple[str, float, str]]) -> None:
    """
    Function used to show an ordered list of ais

    parameters:
        - list_of_ai: list of tuple as : (ai_name, ai_score), in which the 1st ai as the best scoreand so on
    """
    for ai_name, ai_score, params in list_of_ai:
        print(params)
        st.metric(label=ai_name, value=ai_score, help=params)


def show_best_ai_graph(list_of_ais: list[tuple[str, float]]) -> None:
    if list_of_ais:
        labels = [i[0] for i in list_of_ais]
        values = [i[1] for i in list_of_ais]
        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, hovertemplate="%{label}<br>Score: %{value:.2f}<extra></extra>")]
        )
        st.plotly_chart(fig)


def main() -> None:
    """
    This is the code used to show the form and used by the user to fill it
    """
    st.set_page_config(page_title="Result page", page_icon="🔍")
    st.title("🔍 Result")

    app = get_application()
    list_user = app.get_all_user()
    selected_user = select_user(list_user)
    if not selected_user:
        return
    all_user = selected_user == "<All user>"

    exp = app.get_experiment_from_user(selected_user, all_user)
    if exp is None:
        st.warning(f"There is no mlflow server running on port {config('URI').rsplit(':', 1)[-1]}")
        return
    list_experiments, list_ids = exp
    if not list_experiments:
        st.warning("There is no experiment for this user")
        return
    selected_experiment = select_experiment(list_experiments, list_ids)
    if not selected_experiment:
        return

    val = app.get_ai_from_experiment(selected_experiment)
    if val is None:
        st.warning("There is no runs done for this experiment, or no correct runs.")
        return
    ranked_ais = val
    show_ordered_ais(ranked_ais)
    show_best_ai_graph(ranked_ais)


if __name__ == "__main__":
    main()
