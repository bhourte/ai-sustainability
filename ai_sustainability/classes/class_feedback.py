"""
Class for feedback page,
Streamlit class

methods:
    -display_feedbacks (Admin only)
    - inputs_feedback (User only)
    
"""
import streamlit as st

from ai_sustainability.classes.utils_streamlit import check_user_connected


class FeedbackStreamlit:
    """
    Class used to show all the streamlit UI for the Form page

    Methods :
        - __init__ : initialise the UI and check if the user is connected
    """

    def __init__(self, database_link) -> None:
        self.database_link = database_link

        st.set_page_config(page_title="Feedback Page", page_icon="💬")
        st.title("💬Feedback")
        self.username = check_user_connected()
