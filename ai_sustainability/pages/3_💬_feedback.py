import streamlit as st
from class_form import Form
from decouple import config


def main():
    """
        This is the code used by the user to give feedback and by the Admin to see all feedback
    """
    st.set_page_config(page_title="Feedback Page", page_icon="💬")
    st.title("💬Feedback")
    if 'username' not in st.session_state or st.session_state.username == "":  # User not connected, don't show the page, ask for connection
        st.caption("❌ You are not connected, please connect with your username in the Connection page.")
        return None
    username = st.session_state.username
    # Connection to the online gremlin database via class_from.py
    form = Form(
            endpoint = "questions-db.gremlin.cosmos.azure.com",
            database_name = "graphdb",
            container_name = config('DATABASENAME'),
            primary_key= config('PRIMARYKEY'),
        )
    # Connected as an User
    if username != 'Admin':
        st.caption("✅ Connected as " + str(st.session_state.username))
        username = st.session_state.username
        
        username_exists = form.run_gremlin_query("g.V('"+username+"')")  # check if the user already exist in the database
        if username_exists:
            st.write("Welcome back "+username)
            st.write("You can now give us your feedback")
            text = st.text_area("Your feedback: ")  # text area for the feedback
            if text:
                form.save_feedback(text, username)  # we save the feedback
                st.write("Your feedback has been saved")
                st.write("Thank you for your this !")
        else:
            st.write("You have to fill the form first")
            st.write("Please fill the form first and come back to give us your feedback")
            st.write("Thank you")
    # Connected as an Admin
    else:
        st.caption("🔑 Connected as an Admin")
        form.get_all_feedbacks()

if __name__ == "__main__":
      main()