"""
This file contains the class DbConnection, used to connect to the database and to run the queries
"""
import heapq
import time

import numpy as np
import streamlit as st
from decouple import config
from gremlin_python import statics
from gremlin_python.driver import client, serializer

_range = range
statics.load_statics(globals())

FIRST_NODE_ID = "1"


class dbInterface:
    def __init__(self) -> None:
        pass

    def close(self) -> None:
        """
        Close the connection to the database
        """
        pass

    def run_gremlin_query(self, query: str) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")

        Return :
            - result : the result of the query (list)
        """
        pass

    def get_question_text(self, question_id: str) -> str:
        """
        Get the text of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result[0] : the text of the question (str)
        """
        pass

    def get_answers_text(self, question_id: str) -> list:
        """
        Get the texts of answers of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result : the texts of the answers (list of str)
        """
        pass

    def get_help_text(self, question_id: str) -> str:
        """
        Get the help text of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - help_text : the help text of the question (str)
        """
        pass  # TODO : split function into get_help_text_node and get_help_text_edge

    def get_question_label(self, question_id: str) -> str:
        """
        Get the label of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result[0] : the label of the question (str)
        """
        pass

    def get_next_question(self, answers: list) -> str:
        """
        Get the id of the next question

        Parameters :
            - answers : list of the answers given by the user (list of list of str)  # TODO mettre ça dans le fichier models.py

        Return :
            - result[0] : the id of the next question (str)
        """
        pass

    def check_user_exist(self, username: str) -> bool:
        """
        Check if a user exists in the database

        Parameters :
            - username : the username of the user (str)
        """
        pass

    def check_node_exist(self, node_id: str) -> bool:
        """
        Check if a node exists in the database

        Parameters :
            - node_id : the id of the node (str)
        """
        pass  # TODO : change the function in get_node and if list empty

    def create_user_node(self, username: str) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (str)
        """
        pass

    def get_all_users(self) -> list:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """
        pass

    def get_all_feedbacks(self) -> dict:
        """
        Return all feedbacks from all users in the database
            Return :
                - all_feedbacks : dict of all feedbacks  # TODO mettre ça dans le fichier models.py
                    Dict {
                            username: [feedback1, feedback2, ...]
                    }
        """
        pass

    def get_user_feedbacks(self, username: str) -> list:
        """
        Return all feedbacks from a user in the database
            Return :
                - result : list of all feedbacks from a user (list of str)
        """
        pass

    def save_feedback(self, username: str, feedback: str) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        pass

    def create_feedback_node(self, username: str) -> None:
        """
        Create a feedback node in the database

        Parameters :
            - username : the username of the user (str)
        """
        pass

    def create_feedback_edge(self, username: str, feedback: str) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        pass

    def get_nb_feedback_from_user(self, username: str) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (str)

        Return :
            - result[0] : the number of feedbacks from a user (int)
        """
        pass

    def get_nb_selected_edge(self) -> dict:
        """
        Return a dict with number of selected edge for each proposition

        Return :
            - nb_selected_edge : dict of number of selected edge for each proposition
                Dict{ edge_id: [text, nb_selected]}  # TODO mettre ça dans le fichier models.py
        """
        pass  # TODO : remove and decompose

    def get_nb_selected_edge_stats(self) -> dict:
        """
        Return a dict with number of selected edge for each proposition
        Especially for stats showing
        Return :
            - nb_selected_edge : dict of number of selected edge for each proposition
                Dict{ edge_id: [text, nb_selected]}  # TODO mettre ça dans le fichier models.py
        """
        pass  # TODO : remove

    def check_form_exist(self, username: str, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """
        pass  # TODO : remove because get_node

    def get_weight(self, edge_id: str) -> list[float]:
        """
        Get the list_coef from the edge with edge_id id

        Parameters:
            - edge_id (str): id of the edge in the db

        Return:
            - list_weight (list(float)): list of the weights of the edge  # TODO mettre ça dans le fichier models.py(à voir s'il faut le faire ou pas)
        """
        pass

    def get_edges_id(self, answers: list) -> list:
        """
        Get the edges id of the answers

        Parameters:
            - answers (list): list of the answers of the user

        Return:
            - edges_id (list): list of the edges id of the answers of the user
        """
        pass

    def save_answers(self, username: str, form_name: str, answers: list) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user

        Return:
            - bool: True if the answers are saved, False if the form already exist
        """
        pass

    def create_answer_node(self, question_id: str, new_node_id: str) -> None:
        """
        Create a question node in the database

        Parameters:
            - question_id (str): id of the question
            - new_node_id (str): id of the new node
        """
        pass

    def create_answer_edge(self, source_node_id: str, target_node_id: str, answers: list, question_id: str) -> None:
        """
        Create an edge between two nodes

        Parameters:
            - source_node_id (str): id of the source node
            - target_node_id (str): id of the target node
            - answers (list): list of the answers of the user
            - question_id (str): id of the question form
        """
        pass

    def change_answers(self, answers: list, username: str, form_name: str, new_form_name: str) -> bool:
        """
        Change the answer in db

        Parameters:
            - answers (list): list of answers
            - username (str): username of the user
            - form_name (str): name of the form
            - new_form_name (str): new name of the form

        Return:
            - bool: True if the answers are saved, False if the form already exist
        """
        pass

    def get_proposition_id(self, source_node_id: str, answer: str) -> str:
        """
        Get the id of a proposition

        Parameters:
            - source_node_id (str): id of the source node
            - answer (str): answer of the user

        Return:
            - str: id of the proposition
        """
        pass

    def get_all_forms(self, username: str) -> list:
        """
        Get all the forms of a user

        Parameters:
            - username (str): username of the user

        Return:
            - list: list of the forms_id
        """
        pass

    def get_list_answers(self, selected_form: str) -> list:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list: list of the answers
        """
        pass
