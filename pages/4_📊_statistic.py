import streamlit as st
from class_form import Form
from decouple import config

def main():
    """
        This is the code used by the admin to see statistics from the answers of the users
    """
    st.set_page_config(page_title="Statistic Page", page_icon="📊")
    st.title("📊Statistic")
    if 'username' not in st.session_state or st.session_state.username == "":  # User not connected, don't show the stat, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    # Connection to the online gremlin database via class_from.py
    form = Form(endpoint="questions-db.gremlin.cosmos.azure.com", database_name="graphdb", container_name=config('DATABASENAME'), primary_key= config('PRIMARYKEY'),)
    if username != 'Admin':  # Not a admin, we don't show anything
        st.caption("❌ Connected as " + str(username))
        st.write("You are not an Admin")
        st.write("You can't access to this page")
    else:  # connected as an Admin
        st.caption("🔑 Connected as an " + str(username))
        st.write("Welcome Admin")
        st.write("You can now see the statistic of the form")
        selected_edges = form.get_nb_selected_edges()
        form.display_bar_graph(selected_edges)  # graph 1 of stat
        form.display_bar_graph_v2(selected_edges)  # graph 2 of stat

if __name__ == "__main__":
    main()