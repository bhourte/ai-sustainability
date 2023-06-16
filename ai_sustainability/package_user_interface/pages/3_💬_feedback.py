"""
This file is used to show the Feedback page
"""
import streamlit as st

from ai_sustainability.package_user_interface.pages_elements.page_feedback import (
    FeedbackPage,
)


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    st.set_page_config(page_title="Feedback Page", page_icon="💬")
    st.title("💬Feedback")
    st_feedback = FeedbackPage()
    username = st_feedback.username
    if not username:
        return
    st_feedback.render()


if __name__ == "__main__":
    main()
