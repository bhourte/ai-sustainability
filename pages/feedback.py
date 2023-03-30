import streamlit as st
from class_form import Form
from decouple import config
def main():
    st.title("Feedback")
    if 'username' not in st.session_state or st.session_state.username == "":  # Not connected
        st.caption("You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    if username != 'Admin':  # Connected as an User
        st.caption("Connected as " + str(st.session_state.username))
        username = st.session_state.username
        form = Form(
            endpoint = "questions-db.gremlin.cosmos.azure.com",
            database_name = "graphdb",
            container_name = 'Form',
            primary_key= config('PRIMARYKEY'),
        )
        username_exists = form.run_gremlin_query("g.V('"+username+"')")
        if username_exists:
            st.write("Welcome back "+username)
            st.write("You can now give us your feedback")
            text = st.text_area("Your feedback: ")
            if text:
                form.save_feedback(text, username)
                st.write("Your feedback has been saved")
                st.write("Thank you for your this !")
        else:
            st.write("You have to fill the form first")
            st.write("Please fill the form first and come back to give us your feedback")
            st.write("Thank you")
    else:  # Connected as an Admin
        st.caption("Connected as an Admin")
        # Code pour l'admin ici

if __name__ == "__main__":
      main()