"""
This file is used to show the Feedback page
"""
from ai_sustainability.classes.class_feedback import FeedbackStreamlit
from ai_sustainability.package_data_access.db_connection import DbConnection


def main() -> None:
    """
    This is the code used by the user to give feedback and by the Admin to see all feedback
    """

    st_feedback = FeedbackStreamlit()
    database = DbConnection()
    username = st_feedback.username
    if not username:
        return

    # Connected as an User
    if username != "Admin":
        if not database.check_user_exist(username):  # check if the user already exist in the database
            st_feedback.user_dont_exist()
            return
        feedback_text = st_feedback.feedback_box(username)
        if feedback_text:
            database.save_feedback(username, feedback_text)  # we save the feedback
    # Connected as an Admin
    else:
        all_feedbacks = database.get_all_feedbacks()
        st_feedback.show_all_feedbacks(all_feedbacks)


if __name__ == "__main__":
    main()
