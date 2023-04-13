"""
File with our Application class
"""
import streamlit as st

from ai_sustainability.package_business.business import Business
from ai_sustainability.package_data_access.db_connection import DbConnection
from ai_sustainability.utils.models import (
    AnswersList,
    Feedback,
    Question,
    SelectedEdge,
    User,
    UserFeedback,
)


@st.cache_resource
def connec_to_db() -> DbConnection:
    return DbConnection()


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
        - get_list_answers
        - get_all_feedbacks
        - get_nb_selected_edge_stats
        - check_user_exist
        - check_form_exist
        - save_answers
        - change_answers
        - save_feedback
    """

    def __init__(self) -> None:
        self.database = connec_to_db()
        self.business = Business()
        self.list_questions: list[Question] = []
        self.modif_crypted = False

    def get_next_question(self, answer_list: AnswersList) -> Question:
        """
        Get the id of the next question

        Parameters :
            - answer : all answers given by the user for the question

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """
        if len(answer_list) < len(self.list_questions):
            self.list_questions = self.list_questions[: len(answer_list)]
        if not answer_list:  # The form is empty, so we create a question 0 to initialise it
            start = Question(question_id="0", text="", type="start", help_text="", answers=[])
            self.list_questions.append(self.database.get_next_question(start, []))
            return self.list_questions[-1]

        actual_question = self.list_questions[-1]
        if len(answer_list) > 1 and answer_list[1][0].text == "Yes":
            self.modif_crypted = True
        next_question = self.database.get_next_question(actual_question, answer_list[-1])
        if self.modif_crypted:
            list_proposition = []
            for i in next_question.answers:
                if not i.modif_crypted:
                    list_proposition.append(i)
            next_question.answers = list_proposition
        self.list_questions.append(next_question)
        return next_question

    def calcul_best_ais(self, nb_ai: int, answers: AnswersList) -> list[str]:
        """
        Calculate the name best AI to use for the user

        Parameters:
            - nb_ai (int): number of AI to return
            - answers (list): list of the answers of the user
        """
        list_ai = self.database.get_all_ais()  # We get all existing AIs
        return self.business.calcul_best_ais(nb_ai=nb_ai, list_ai=list_ai, list_answers=answers)

    def get_best_ais(self, username: User, form_name: str) -> list[str]:
        """
        Method used to retreive all the N_best Ais stored in a answer
        """
        return self.database.get_best_ais(username, form_name)

    def get_all_users(self) -> list[User]:
        """
        Return all users in the database
        """
        return self.database.get_all_users()

    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user
        """
        return self.database.get_all_forms_names(username)

    def get_list_answers(self, username: User, selected_form: str) -> AnswersList:
        """
        Get the list of answers of a form
        """
        return self.database.get_list_answers(username, selected_form)

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """
        return self.database.get_all_feedbacks()

    def get_nb_selected_edge_stats(self) -> list[SelectedEdge]:
        """
        Return a list with all existing edges and the number of time they had been selected
        Used in stats showing
        """
        return self.database.get_nb_selected_edge()

    def check_user_exist(self, username: User) -> bool:
        return self.database.check_node_exist(username)

    def check_form_exist(self, username: User, form_name: str) -> bool:
        """
        Check if a form exist for a specific user in the database
        """
        return self.database.check_node_exist(f"{username}-answer1-{form_name}")

    def save_answers(self, username: User, form_name: str, answers: AnswersList, list_best_ai: list[str]) -> bool:
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
        return self.database.save_answers(username, form_name, answers, self.list_questions, list_best_ai)

    def change_answers(
        self, answers: AnswersList, username: User, form_name: str, new_form_name: str, list_best_ai: list[str]
    ) -> bool:
        """
        Change the answer in db

        Parameters:
            - answers (list): list of answers
            - username (str): username of the user
            - form_name (str): name of the form
            - new_form_name (str): new name of the form
            - list_best_ai (list[str]): list of the n best AIs selected for this form

        Return:
            - bool: True if the answers are well saved, False if the form already exist
        """
        return self.database.change_answers(
            answers, username, form_name, new_form_name, self.list_questions, list_best_ai
        )

    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        self.database.save_feedback(username, feedback)
