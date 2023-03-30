import streamlit as st
from class_form import Form
from decouple import config


def main():
    st.title("Historic")
    if 'username' not in st.session_state or st.session_state.username == "":
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    st.caption("Connected as " + str(username))

    form = Form(
            endpoint = "questions-db.gremlin.cosmos.azure.com",
            database_name = "graphdb",
            container_name = 'Persons',
            primary_key= config('PRIMARYKEY'),
        )

if __name__ == "__main__":
      main()