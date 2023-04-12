"""
This file contains the interface for all database connection classes,
used to connect to the database and to run the queries
"""
from abc import ABC, abstractmethod

from ai_sustainability.utils.models import (
    AnswersList,
    Feedback,
    Query,
    Question,
    SelectedEdge,
    User,
    UserAnswers,
    UserFeedback,
)


class DBInterface(ABC):
    """
    Interface for all class that has to connect to a database
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the database
        """

    ########## Useful method ##########

    @abstractmethod
    def run_gremlin_query(self, query: Query) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")

        Return :
            - list of all result that correspond to the query (list)
        """

    @abstractmethod
    def get_next_question(self, actual_question: Question, answer: UserAnswers) -> Question:
        """
        Get the id of the next question

        Parameters :
            - actual_question : the actual Question
            - answer : the answer given by the user for the question (if "" : this means no specific answer eg: Q_Next)

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """

    @abstractmethod
    def create_user_node(self, username: User) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (str)
        """

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """

    @abstractmethod
    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """

    @abstractmethod
    def get_user_feedbacks(self, username: User) -> UserFeedback:
        """
        Return all feedbacks from a user in the database
        """

    @abstractmethod
    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """

    @abstractmethod
    def create_feedback_edge(self, username: User, feedback: Feedback) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """

    @abstractmethod
    def get_nb_feedback_from_user(self, username: User) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (str)

        Return :
            - the number of feedbacks from a user (int)
        """

    @abstractmethod
    def get_weight(self, edge_id: str) -> list[float]:
        """
        Get the list_coef from the edge with edge_id id

        Parameters:
            - edge_id (str): id of the edge in the db

        Return:
            - list of the weights of the edge
        """

    @abstractmethod
    def save_answers(self, username: User, form_name: str, answers: AnswersList, questions: list[Question]) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user

        Return:
            - True if the answers are saved, False if the form already exist
        """

    @abstractmethod
    def create_answer_node(self, question: Question, new_node_id: str) -> None:
        """
        Create a question node in the database

        Parameters:
            - question_id (str): id of the question
            - new_node_id (str): id of the new node
        """

    @abstractmethod
    def create_answer_edges(
        self,
        source_node_id: str,
        target_node_id: str,
        answers: UserAnswers,
    ) -> None:
        """
        Create an edge between two nodes

        Parameters:
            - source_node_id (str): id of the source node
            - target_node_id (str): id of the target node
            - answers (list): list of the answers of the user
            - question_id (str): id of the question form
        """

    @abstractmethod
    def change_answers(self, answers: AnswersList, username: User, form_name: str, new_form_name: str) -> bool:
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
    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (str): username of the user

        Return:
            - list of the forms_id
        """

    @abstractmethod
    def get_list_answers(self, selected_form: str) -> AnswersList:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list of the answers
        """

    ########## Less useful method ##########  TODO : see if we keep them

    @abstractmethod
    def get_nb_selected_edge(self) -> list[SelectedEdge]:
        """
        Return a dict with number of selected edge for each proposition

        Return :
            - number of selected edge for each proposition
        """
