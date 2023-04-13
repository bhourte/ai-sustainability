"""
This file contains the interface for all database connection classes,
used to connect to the database and to run the queries
"""
from abc import ABC, abstractmethod

from ai_sustainability.utils.models import (
    AnswersList,
    Feedback,
    Proposition,
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

    @abstractmethod
    def run_gremlin_query(self, query: Query) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (Query) (Exemple : Query("g.V()"))

        Return :
            - list of all result that correspond to the query (list)
        """

    @abstractmethod
    def get_next_question(self, actual_question: Question, answer: UserAnswers) -> Question:
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
    def get_propositions(self, question_id: str) -> list[Proposition]:
        """
        Get the propositions for a question in the database

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - propositions : list of all propositions for the question (list of Proposition)
        """

    @abstractmethod
    def create_user_node(self, username: User) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (User)
        """

    @abstractmethod
    def get_all_users(self) -> list[User]:
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
    def get_user_feedbacks(self, username: User) -> UserFeedback:
        """
        Return all feedbacks from a user in the database

        Parameters :
            - username : the username of the user (User)

        Return :
            - result : list of all feedbacks from the user (UserFeedback)
        """

    @abstractmethod
    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (User)
            - feedback : the feedback given by the user (Feedback)
        """

    @abstractmethod
    def check_feedback_exist(self, username: User) -> bool:
        """
        Check if a feedback exist in the database

        Parameters :
            - username : the username of the user (User)

        Return :
            - bool : True if the feedback exist, False otherwise
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
    def create_feedback_node(self, username: User) -> None:
        """
        Create a feedback node in the database

        Parameters :
            - username : the username of the user (User)
        """

    def create_feedback_edge(self, username: User, feedback: Feedback) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (User)
            - feedback : the feedback given by the user (Feedback)
        """

    @abstractmethod
    def get_nb_feedback_from_user(self, username: User) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (User)

        Return :
            - the number of feedbacks from a user (int)
        """

    @abstractmethod
    def save_answers(
        self, username: User, form_name: str, answers: AnswersList, questions: list[Question], best_ais: list[str]
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
    def create_answer_node(self, question: Question, new_node_id: str) -> None:
        """
        Create a question node in the database

        Parameters:
            - question (Question): id of the question
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
            - answers (UserAnswers): list of the answers of the user
        """

    @abstractmethod
    def change_answers(
        self,
        answers: AnswersList,
        username: User,
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
    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (User): username of the user

        Return:
            - list of the forms_id
        """

    @abstractmethod
    def get_list_answers(self, username: User, form_name: str) -> AnswersList:
        """
        Get the list of answers of a form

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form

        Return:
            - list_answers (AnswersList): list of the answers
        """

    @abstractmethod
    def get_answers(self, node_id: str) -> list[Proposition]:
        """
        Get the answers of a node (completed form)

        Parameters:
            - node_id (str): id of the node

        Return:
            - list of the answers (list[Proposition])
        """

    @abstractmethod
    def get_node_label(self, node_id: str) -> str:
        """
        Get the label of a node

        Parameters:
            - node_id (str): id of the node

        Return:
            - label of the node (str)
        """

    @abstractmethod
    def get_nb_selected_edge(self) -> list[SelectedEdge]:
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
    def get_best_ais(self, username: User, form_name: str) -> list[str]:
        """
        Return the best ais for a form which was saved in the db

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form

        Return:
            - list of the best ais (list[str])
        """
