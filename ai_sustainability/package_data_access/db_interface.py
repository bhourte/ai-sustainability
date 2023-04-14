"""
This file contains the interface for all database connection classes,
used to connect to the database and to run the queries
"""
from abc import ABC, abstractmethod

from ai_sustainability.package_business.models import (
    AnswersList,
    Edge,
    Feedback,
    FormAnswers,
    Question,
    UserFeedback,
    Username,
)


class DBInterface(ABC):
    """
    Interface for all class that has to connect to a database
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_next_question(self, actual_question: Question, answer: AnswersList) -> Question:
        """
        get the next question

        Parameters :
            - actual_question : the actual Question (Question)
            - answer : the answer given by the user for the question (UserAnswers)

        Return :
            - a Question corresponding to the next question according to
                the actual_question and answer provided (Question)
        """

    @abstractmethod
    def get_all_users(self) -> list[Username]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of User)
        """

    @abstractmethod
    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks in the database

        Return :
            - result : list of all feedbacks (list of UserFeedback)
        """

    @abstractmethod
    def save_feedback(self, username: Username, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (User)
            - feedback : the feedback given by the user (Feedback)
        """

    @abstractmethod
    def check_node_exist(self, node_id: str) -> bool:
        """
        Check if a node exists in the database

        Parameters :
            - node_id : the id of the node (str)

        Return :
            - bool : True if the node exists, False otherwise
        """

    @abstractmethod
    def save_answers(
        self, username: Username, form_name: str, answers: FormAnswers, questions: list[Question], best_ais: list[str]
    ) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form
            - answers (AnswerList): list of the answers of the user
            - questions (list[Question]): list of the questions of the form
            - best_ais (list[str]): list of the best ais

        Return:
            - True if the answers are saved, False if the form already exist
        """

    @abstractmethod
    def check_form_exist(self, username: str, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """

    @abstractmethod
    def update_answers(
        self,
        answers: FormAnswers,
        username: Username,
        form_name: str,
        new_form_name: str,
        questions: list[Question],
        best_ais: list[str],
    ) -> bool:
        """
        Change the answer in db

        Parameters:
            - answers (list): list of answers
            - username (str): username of the user
            - form_name (str): name of the form
            - new_form_name (str): new name of the form

        Return:
            - True if the answers are saved, False if the form already exist
        """

    @abstractmethod
    def get_all_forms_names(self, username: Username) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (User): username of the user

        Return:
            - list of the forms_id
        """

    @abstractmethod
    def get_list_answers(self, username: Username, form_name: str) -> FormAnswers:
        """
        Get the list of answers of a form

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form

        Return:
            - list_answers (AnswersList): list of the answers
        """

    @abstractmethod
    def get_nb_selected_edge(self) -> list[Edge]:
        """
        Return a list of SelectedEdge with theb number of times edge was selected for each proposition

        Return :
            - selected_edges (list[SelectedEdge]) : list of SelectedEdge
        """

    @abstractmethod
    def get_all_ais(self) -> list[str]:
        """
        Get all the ais in the db

        Return:
            - list of the ais (list[str])
        """

    @abstractmethod
    def get_best_ais(self, username: Username, form_name: str) -> list[str]:
        """
        Return the best ais for a form which was saved in the db

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form

        Return:
            - list of the best ais (list[str])
        """
