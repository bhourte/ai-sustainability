"""
Class for feedback page,
Streamlit class
"""
import streamlit as st

from ai_sustainability.package_application.application import Application
from ai_sustainability.package_business.models import Feedback, UserFeedback, Username
from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
)
from ai_sustainability.utils import sanitize_text_input


class FeedbackStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - render
        - show_all_feedbacks
        - show_user_feedback
        - warn_unexisting_user
        - retrieve_user_feedback : show a box where the user can give a feedback
        - retrieve_feedback
    """

    def __init__(self, app: Application) -> None:
        self.app = app
        self.username = check_user_connection()
        st.session_state.clicked = False

    def render(self) -> None:
        if self.username == "Admin":
            return self.show_all_feedbacks()

        if not self.app.user_exist(self.username):
            return self.warn_unexisting_user()

        self.retrieve_user_feedback()

    def show_all_feedbacks(self) -> None:
        all_feedbacks = self.app.get_all_feedbacks()
        print(all_feedbacks)
        if not all_feedbacks:
            st.write("There is no user in the database.")
            return
        has_feedback = [self.show_user_feedback(user_feedback) for user_feedback in all_feedbacks]
        if not any(has_feedback):
            st.write("There is no feedback in the database.")

    def show_user_feedback(self, user_feedback: UserFeedback) -> bool:
        print(user_feedback)
        with st.expander("Feedbacks from " + user_feedback.user):
            for index, value in enumerate(user_feedback.feedbacks):
                st.write(f"feedback {index+1} : {value}")
        return bool(user_feedback.feedbacks)

    def warn_unexisting_user(self) -> None:
        st.write("You have never filled out a form.")
        st.write("Please fill the form first and come back to give us your feedback.")
        st.write("Thank you")

    def retrieve_user_feedback(self) -> None:
        feedback_text = self.retrieve_feedback(self.username)
        if feedback_text:
            self.app.save_feedback(self.username, feedback_text)

    def retrieve_feedback(self, username: Username) -> Feedback:
        """
        Method used to show a box where the user can give a feedback
        """
        st.write(f"Welcome back {username}")
        st.write("You can now give us your feedback")
        text = st.text_area("Your feedback: ")
        if not text:
            return Feedback("")
        st.write("Your feedback has been saved")
        st.write("Thank you!")
        return Feedback(sanitize_text_input(text))
