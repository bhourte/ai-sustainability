"""
This file is used to show the Feedback page
"""
import streamlit as st
from decouple import config

from ai_sustainability.class_form_old import Form
from ai_sustainability.classes.class_feedback import FeedbackStreamlit
from ai_sustainability.classes.db_connection import DbConnection


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    database = object()  # TODO mettre ici le lien vers la database
    st_form = FeedbackStreamlit(database)
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

    # Connected as an User
    if username != "Admin":
        username_exists = form.run_gremlin_query(
            "g.V('" + username + "')"
        )  # check if the user already exist in the database
        if not username_exists:
            st.write("You have to fill the form first")
            st.write("Please fill the form first and come back to give us your feedback")
            st.write("Thank you")
            return
        st.write("Welcome back " + username)
        st.write("You can now give us your feedback")
        text = st.text_area("Your feedback: ")  # text area for the feedback
        if not text:
            return
        form.save_feedback(text, username)  # we save the feedback
        st.write("Your feedback has been saved")
        st.write("Thank you for your this !")

    # Connected as an Admin
    else:
        form.get_all_feedbacks()


def main_new() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    database = DbConnection()
    st_feedback = FeedbackStreamlit(database)
    username = st_feedback.username
    if not username:
        return

    # Connected as an User
    if username != "Admin":
        username_exists = database.check_user_exist(username)  # check if the user already exist in the database
        if not username_exists:
            st_feedback.user_dont_exist()
            return
        feedback_text = st_feedback.feedback_box(username)
        if not feedback_text:
            return
        database.save_feedback(username, feedback_text)  # we save the feedback
    # Connected as an Admin
    else:
        all_feedbacks = database.get_all_feedbacks()
        st_feedback.show_all_feedbacks(all_feedbacks)


if __name__ == "__main__":
    main_new()
