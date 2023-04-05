"""
This file is used to show the Statistic page
"""
import streamlit as st
from decouple import config

from ai_sustainability.class_form_old import Form
from ai_sustainability.classes.class_statistic import StatisticStreamlit


def main() -> None:
    """
    This is the code used by the admin to see statistics from the answers of the users
    """

    database = None  # TODO mettre ici le lien vers la database
    st_form = StatisticStreamlit(database)
    username = st_form.username
    if not username:
        return

    # Connection to the online gremlin database via class_from.py
    form = Form(
        endpoint="questions-db.gremlin.cosmos.azure.com",
        database_name="graphdb",
        container_name=config("DATABASENAME"),
        primary_key=config("PRIMARYKEY"),
    )
    if username != "Admin":  # Not a admin, we don't show anything
        st.write("You are not an Admin")
        st.write("You can't access to this page")
    else:  # connected as an Admin
        st.write("Welcome Admin")
        st.write("You can now see the statistic of the form")
        selected_edges = form.get_nb_selected_edges()
        with st.spinner("Loading..."):
            form.display_bar_graph(selected_edges)  # graph 1 of stat
        with st.spinner("Loading..."):
            form.display_bar_graph_v2(selected_edges)  # graph 2 of stat


if __name__ == "__main__":
    main()
