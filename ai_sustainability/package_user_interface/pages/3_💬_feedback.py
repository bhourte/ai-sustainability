"""
This file is used to show the Feedback page
"""
from ai_sustainability.package_application.application import Application
from ai_sustainability.package_user_interface.classes.class_feedback import (
    FeedbackStreamlit,
)


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    st_feedback = FeedbackStreamlit()
    app = Application()
    username = st_feedback.username
    if not username:
        return

    # Connected as an User
    if username != "Admin":
        if not app.check_user_exist(username):  # check if the user already exist in the database
            st_feedback.user_dont_exist()
            return
        feedback_text = st_feedback.feedback_box(username)
        if feedback_text:
            app.save_feedback(username, feedback_text)  # we save the feedback
    # Connected as an Admin
    else:
        all_feedbacks = app.get_all_feedbacks()
        st_feedback.show_all_feedbacks(all_feedbacks)


if __name__ == "__main__":
    main()
