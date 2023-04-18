"""
File with our Application class
"""
from decouple import config

from ai_sustainability.package_business.models import (
    AnswersStats,
    Feedback,
    Form,
    Question,
    UserFeedback,
    Username,
)
from ai_sustainability.package_data_access.db_connection import DbConnection


class Application:
    """
    Class used to make the link between the database and the UI

    Methods :
        - __init__
        - get_next_question
        - calcul_best_ais
        - get_best_ais
        - get_all_users
        - get_all_forms_names
        - get_previous_form
        - get_all_feedbacks
        - get_nb_selected_edge_stats
        - check_user_exist
        - check_form_exist
        - save_answers
        - save_feedback
    """

    def __init__(self, database: DbConnection) -> None:
        self.database = database

    def get_next_question(self, form: Form, question_number: int) -> Question:
        """
        Get the id of the next question

        Parameters :
            - answer : all answers given by the user for the question

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """
        return self.database.get_next_question(form, question_number)

    def calcul_best_ais(self, form: Form) -> list[str]:
        """
        Calculate the name best AI to use for the user

        Parameters:
            - nb_ai (int): number of AI to return
            - answers (list): list of the answers of the user
        """
        list_ai = self.database.get_all_ais()  # We get all existing AIs
        nb_ai = int(config("NBEST_AI"))
        return form.calcul_best_ais(nb_ai=nb_ai, list_ai=list_ai)

    def get_best_ais(self, username: Username, form_name: str) -> list[str]:
        """
        Method used to retreive all the N_best Ais stored in a answer
        """
        return self.database.get_best_ais(username, form_name)

    def get_all_users(self) -> list[Username]:
        """
        Return all users in the database
        """
        return self.database.get_all_users()

    def get_all_forms_names(self, username: Username) -> list[str]:
        """
        Get all names of the forms of a user
        """
        return self.database.get_all_forms_names(username)

    def get_previous_form(self, username: Username, selected_form: str) -> Form:
        """
        Get the list of answers of a form
        """
        return self.database.get_previous_form(username, selected_form)

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """
        return self.database.get_all_feedbacks()

    def get_nb_selected_answer_stats(self) -> list[AnswersStats]:
        """
        Return a list with all existing edges and the number of time they had been selected
        Used in stats showing
        """
        return self.database.get_nb_selected_edge()

    def user_exist(self, username: Username) -> bool:
        return self.database.check_node_exist(username)

    def check_form_exist(self, username: Username, form_name: str) -> bool:
        """
        Check if a form exist for a specific user in the database
        """
        return self.database.check_node_exist(f"{username}-answer1-{form_name}")

    def save_answers(self, form: Form, list_best_ai: list[str], new_form_name: str = "") -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user
            - list_best_ai (list[str]): list of the n best AIs selected for this form

        Return:
            - bool: True if the answers are well saved, False if the form already exist
        """
        return self.database.save_answers(form, list_best_ai, new_form_name)

    def save_feedback(self, username: Username, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        self.database.save_feedback(username, feedback)
