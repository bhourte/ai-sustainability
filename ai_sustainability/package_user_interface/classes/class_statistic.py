"""
Class for statistic page
Streamlit class
"""
import plotly.graph_objects as go
import streamlit as st

from ai_sustainability.package_business.models import Edge
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
)


class StatisticStreamlit:  # TODO rename stat_page
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - check_if_admin : chek if the user is an admin, show some messages in both cases
        - display_statistic_edges : show stats based on the edges
        - display_statistic_ais : show stats based on the AIs (not implemented yet)
    """

    def __init__(self) -> None:
        st.set_page_config(page_title="Statistic Page", page_icon="📊")  # TODO put in render
        st.title("📊Statistic")
        self.username = check_user_connection()
        st.session_state.clicked = False

    def check_if_admin(self, username: str) -> bool:
        if username != "Admin":
            st.write("You are not an Admin")
            st.write("You can't access to this page")
            return False
        st.write("Welcome Admin")
        st.write("You can now see the statistic of the form")
        return True

    def display_answers_statistic(self, edge_selected: list[Edge]) -> None:
        """
        Display bar graph of edges selected

        Parameters:
            - edge_selected: dictionnary with proposition_id as key and number of time it was selected as value
        """
        if not edge_selected:
            st.write("There is no form answered")
            return
        with st.spinner("Loading..."):
            # sort the list on edges name
            edge_selected.sort(key=lambda x: x.answer_id)
            hover_text = [repr(edge) for edge in edge_selected]  # text with the in and out node
            text = [edge.text for edge in edge_selected]  # Text of the selected answer
            count_edges = [edge.nb_selected for edge in edge_selected]  # Number of times each edge was selected
            list_edge_name = sorted({k.answer_id for k in edge_selected})  # To get the edges name in ascending order
            fig = go.Figure(data=[go.Bar(x=list_edge_name, y=list(count_edges), hovertext=text, text=hover_text)])
            fig.update_layout(
                title="Number of times each edge was selected",
                xaxis_title="Edges/Propositions id",
                yaxis_title="Number of times selected",
                yaxis={
                    "dtick": 1,
                },
            )
            st.plotly_chart(fig)

    def display_statistic_ais(self) -> None:
        """
        Show stats based on the AIs (not implemented yet)
        """
