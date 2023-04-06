"""
Class for feedback page,
Streamlit class
"""
import streamlit as st

from ai_sustainability.classes.utils import validate_text_input
from ai_sustainability.classes.utils_streamlit import check_user_connection


class FeedbackStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
        - show_all_feedbacks
        - user_dont_exist
        - feedback_box : show a box where the user can give a feedback
    """

    def __init__(self, database_link) -> None:
        self.database_link = database_link

        st.set_page_config(page_title="Feedback Page", page_icon="💬")
        st.title("💬Feedback")
        self.username = check_user_connection()
        st.session_state.clicked = False

    def show_all_feedbacks(self, all_feedbacks: dict) -> None:
        if len(all_feedbacks.keys()) == 0:
            st.write("There is no feedback in the database.")
            return
        for user in all_feedbacks:
            with st.expander("Feedbacks from " + user):
                i = 1
                for feedback in all_feedbacks[user]:
                    st.write(f"feedback {i} : {feedback}")
                    i += 1

    def user_dont_exist(self) -> None:
        st.write("You have never filled out a form.")
        st.write("Please fill the form first and come back to give us your feedback.")
        st.write("Thank you")

    def feedback_box(self, username: str) -> str:
        """
        Method used to show a box where the user can give a feedback
        """
        st.write("Welcome back " + username)
        st.write("You can now give us your feedback")
        text = st.text_area("Your feedback: ")  # text area for the feedback
        if not text:
            return ""
        st.write("Your feedback has been saved")
        st.write("Thank you for your this !")
        return validate_text_input(text)
