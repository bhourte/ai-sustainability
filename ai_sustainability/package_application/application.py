"""
File with our Application class
"""

from typing import Optional, Tuple

from decouple import config

from ai_sustainability.package_business.launch_mlflow import MlFlow
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
        - user_exist
        - form_exist
        - save_answers
        - save_feedback
        - create_experiment
    """

    def __init__(self, database: DbConnection) -> None:
        self.database = database
        self.mlflow = MlFlow()

    def get_next_question(self, form: Form, question_number: int) -> Question:
        """
        Get the next question

        Parameters :
            - form : the actual Form used by the user
            - <uestion_number

        Return :
            - a Question corresponding to the next question according to the answers given in the Form
        """
        return self.database.get_next_question(form, question_number)

    def calcul_best_ais(self, form: Form) -> list[Tuple[str, float]]:
        """
        Calculate the name best AI to use for the user
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
        Get a already completed Form stord in the DB
        """
        return self.database.retrieve_previous_form(username, selected_form)

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
        """
        Check if a User exist for a specific user in the database
        """
        return self.database.check_node_exist(username)

    def form_exist(self, username: Username, form_name: str) -> bool:
        """
        Check if a Form exist for a specific user in the database
        """
        return self.database.check_node_exist(f"{username}-answer1-{form_name}")

    def save_answers(
        self, form: Form, list_best_ai: list[Tuple[str, float]], mlflow_id: Optional[str] = "", new_form_name: str = ""
    ) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - form : the Form to save in the DB
            - list_best_ai : list of the n best AIs selected for this form
            - new_form_name : the name of the form (if not "", we want to update the Form present in the database)

        Return:
            - bool: True if the answers are well saved, False if the form already exist
        """
        if new_form_name and form.username is not None and form.experiment_id is not None:
            self.change_experiment_name(form.username, form.form_name, new_form_name)
        return self.database.save_answers(form, list_best_ai, mlflow_id, new_form_name)

    def save_feedback(self, username: Username, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user
            - feedback : the feedback given by the user
        """
        self.database.save_feedback(username, feedback)

    def create_experiment(self, username: Username, form_name: str) -> Optional[str]:
        """Method used to create an mlflow experiment and return the experiment ID"""
        name = "experiment-" + username + "-" + form_name
        return self.mlflow.create_experiment(name)

    def change_experiment_name(self, username: Username, old_form_name: str, new_form_name: str) -> Optional[str]:
        """method used to change the name of an mlflow experiment and return the corresponding ID"""
        old_experiment_name = "experiment-" + username + "-" + old_form_name
        new_experiment_name = "experiment-" + username + "-" + new_form_name
        return self.mlflow.change_experiment_name(old_experiment_name, new_experiment_name)
