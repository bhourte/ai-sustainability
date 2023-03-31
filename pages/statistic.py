import streamlit as st
from class_form import Form
from decouple import config

def main():
    st.title("Statistic")
    if 'username' not in st.session_state or st.session_state.username == "":
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    st.caption("Connected as " + str(username))
    form = Form(endpoint="questions-db.gremlin.cosmos.azure.com", database_name="graphdb", container_name=config('DATABASENAME'), primary_key= config('PRIMARYKEY'),)
    if username != 'Admin':
        st.write("You are not an Admin")
        st.write("You can't access to this page")
    else:
        st.write("Welcome Admin")
        st.write("You can now see the statistic of the form")
        selected_edges = form.get_nb_selected_edges()
        form.display_bar_graph(selected_edges)

if __name__ == "__main__":
    main()