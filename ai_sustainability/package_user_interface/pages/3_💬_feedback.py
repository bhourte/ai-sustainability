"""
This file is used to show the Feedback page
"""
import streamlit as st

from ai_sustainability.package_user_interface.classes.page_feedback import FeedbackPage
from ai_sustainability.package_user_interface.utils_streamlit import get_application


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    st.set_page_config(page_title="Feedback Page", page_icon="💬")
    app = get_application()
    st_feedback = FeedbackPage(app)
    username = st_feedback.username
    if not username:
        return
    st_feedback.render()


if __name__ == "__main__":
    main()
