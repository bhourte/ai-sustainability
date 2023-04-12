"""
Class for feedback page,
Streamlit class
"""
import streamlit as st

from ai_sustainability.package_user_interface.utils_streamlit import (
    check_user_connection,
)
from ai_sustainability.utils.models import Feedback, User, UserFeedback
from ai_sustainability.utils.utils import validate_text_input


class FeedbackStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_all_feedbacks
        - user_dont_exist
        - feedback_box : show a box where the user can give a feedback
    """

    def __init__(self) -> None:
        st.set_page_config(page_title="Feedback Page", page_icon="💬")
        st.title("💬Feedback")
        self.username = check_user_connection()
        st.session_state.clicked = False

    def show_all_feedbacks(self, all_feedbacks: list[UserFeedback]) -> None:
        if not all_feedbacks:  # If there is no user in the database
            st.write("There is no user in the database.")
            return
        is_feedback = False
        for user_feedback in all_feedbacks:
            with st.expander("Feedbacks from " + user_feedback.user):
                for index, value in enumerate(user_feedback.feedbacks):
                    st.write(f"feedback {index} : {value}")
                    is_feedback = True
        if not is_feedback:  # If there is no feedback in the database
            st.write("There is no feedback in the database.")

    def user_dont_exist(self) -> None:
        st.write("You have never filled out a form.")
        st.write("Please fill the form first and come back to give us your feedback.")
        st.write("Thank you")

    def feedback_box(self, username: User) -> Feedback:
        """
        Method used to show a box where the user can give a feedback
        """
        st.write(f"Welcome back {username}")
        st.write("You can now give us your feedback")
        text = st.text_area("Your feedback: ")  # text area for the feedback
        if not text:
            return Feedback("")
        st.write("Your feedback has been saved")
        st.write("Thank you!")
        return Feedback(validate_text_input(text))
