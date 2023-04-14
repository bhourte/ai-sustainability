"""
This file is used to show the Feedback page
"""
import streamlit as st

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import Username
from ai_sustainability.package_user_interface.classes.class_feedback import (
    FeedbackStreamlit,
)


def retrieve_user_feedback(app: Application, st_feedback: FeedbackStreamlit, username: Username) -> None:
    feedback_text = st_feedback.retrieve_feedback(username)
    if feedback_text:
        app.save_feedback(username, feedback_text)


def show_all_feedbacks(app: Application, st_feedback: FeedbackStreamlit) -> None:
    all_feedbacks = app.get_all_feedbacks()
    st_feedback.show_all_feedbacks(all_feedbacks)


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    st.set_page_config(page_title="Feedback Page", page_icon="💬")
    st.title("💬Feedback")
    st_feedback = FeedbackStreamlit()
    app = Application()
    username = st_feedback.username
    if not username:
        return

    if username == "Admin":
        return show_all_feedbacks(app, st_feedback)

    if not app.user_exist(username):
        return st_feedback.warn_unexisting_user()

    retrieve_user_feedback(app, st_feedback, username)


if __name__ == "__main__":
    main()
