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
LAST_NODE_ID = "9"


@st.cache_resource
def connect(endpoint: str, database_name: str, container_name: str, primary_key: str) -> client.Client:
    """
    Connect to the database and return the client (made only once thanks to the cache)

    Parameters :
        - endpoint : the endpoint of the database (string)
        - database_name : the name of the database (string)
        - container_name : the name of the container (string)
        - primary_key : the primary key of the database (string)

    Return :
        - client : the client to connect to the database
    """
    return client.Client(
        "wss://" + endpoint + ":443/",
        "g",
        username="/dbs/" + database_name + "/colls/" + container_name,
        password=primary_key,
        message_serializer=serializer.GraphSONSerializersV2d0(),
    )


class DbConnection:
    """
    Class used to connect to the database and to run the queries on it

    Attributes :
        - gremlin_client : the client to connect to the database
        - list_questions_id : list of the questions id already asked to the user (list of str)
        - modif_crypted : boolean to know if the user has already modified the crypted question (bool)
    """

    def __init__(self):
        """
        Initialize the class with the connection to the database
        """
        self.gremlin_client = None
        self.list_questions_id = []
        self.modif_crypted = False

    def make_connection(self):
        """
        Make the connection to the database
        """
        self.gremlin_client = connect(
            endpoint="questions-db.gremlin.cosmos.azure.com",
            database_name="graphdb",
            container_name=config("DATABASENAME"),
            primary_key=config("PRIMARYKEY"),
        )

    def close(self) -> None:
        """
        Close the connection to the database
        """
        self.gremlin_client.close()

    def run_gremlin_query(self, query: str) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")

        Return :
            - result : the result of the query (list)
        """
        run = self.gremlin_client.submit(query).all()
        result = run.result()
        return result

    def get_one_question(self, answers: list) -> dict:
        """
        Get one question from the database

        Parameters :
            - answers : list of the answers given by the user (list of list of str)

        Return :
            - question : dict {
                question_text : the text of the question (str)
                answers : list of answers (list of list of str)
                help_text : the help text of the question (str)
                question_label : the label of the question (str)
            }
        """
        question = {}  # type: dict
        self.truncate_questions(answers)
        question_id = self.get_next_question(answers)
        if question_id == LAST_NODE_ID:
            question["question_text"] = ""
            question["answers"] = []
            question["help_text"] = ""
            question["question_label"] = "end"
            return question

        if len(answers) > 1 and answers[1][0] == "Yes":
            self.modif_crypted = True

        self.list_questions_id.append(question_id)
        question["question_text"] = self.get_question_text(question_id)
        question["answers"] = self.get_answers_text(question_id)
        question["help_text"] = self.get_help_text(question_id)
        question["question_label"] = self.get_question_label(question_id)
        return question

    def get_question_text(self, question_id: str) -> str:
        """
        Get the text of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result[0] : the text of the question (str)
        """
        query = f"g.V('{question_id}').properties('text').value()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_answers_text(self, question_id: str) -> list:
        """
        Get the texts of answers of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result : the texts of the answers (list of str)
        """
        if not self.modif_crypted:
            query = f"g.V('{question_id}').outE().properties('text').value()"
        else:
            query = f"g.V('{question_id}').outE().has('modif_crypted','false').properties('text').value()"
        result = self.run_gremlin_query(query)
        return result

    def get_help_text(self, question_id: str) -> str:
        """
        Get the help text of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - help_text : the help text of the question (str)
        """
        query = f"g.V('{question_id}').properties('help text').value()"
        help_text = self.run_gremlin_query(query)[0]
        if self.modif_crypted:
            query = f"g.V('{question_id}').outE().has('modif_crypted', 'false').properties('help text').value()"
        else:
            query = f"g.V('{question_id}').outE().properties('help text').value()"
        answers_help_text = self.run_gremlin_query(query)
        answers_text = self.get_answers_text(question_id)
        for i, val in enumerate(answers_help_text):
            help_text += f"{answers_text[i]}: {val}"
        return help_text

    def get_question_label(self, question_id: str) -> str:
        """
        Get the label of a question

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - result[0] : the label of the question (str)
        """
        query = f"g.V('{question_id}').label()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_next_question(self, answers: list) -> str:
        """
        Get the id of the next question

        Parameters :
            - answers : list of the answers given by the user (list of list of str)

        Return :
            - result[0] : the id of the next question (str)
        """
        if not answers:
            return FIRST_NODE_ID

        previous_question_id = self.list_questions_id[-1]
        previous_question_label = self.get_question_label(previous_question_id)
        if previous_question_label == "Q_Open" or previous_question_label == "Q_QRM":
            query = f"g.V('{previous_question_id}').outE().inV().id()"
            result = self.run_gremlin_query(query)

        if previous_question_label == "Q_QCM" or previous_question_label == "Q_QCM_Bool":
            query = f"g.V('{previous_question_id}').outE().has('text', '{answers[-1][0]}').inV().id()"
            result = self.run_gremlin_query(query)

        return result[0]

    def truncate_questions(self, answers: list) -> None:
        """
        Truncate the list of questions id if the user has answered less questions than the previous time

        Parameters :
            - answers : list of the answers given by the user (list of list of str)
        """
        if len(answers) < len(self.list_questions_id):
            self.list_questions_id = self.list_questions_id[: len(answers)]

    def check_user_exist(self, username: str) -> bool:
        """
        Check if a user exists in the database

        Parameters :
            - username : the username of the user (str)
        """
        return self.check_node_exist(username)

    def check_node_exist(self, node_id: str) -> bool:
        """
        Check if a node exists in the database

        Parameters :
            - node_id : the id of the node (str)
        """
        query = f"g.V('{node_id}')"
        result = self.run_gremlin_query(query)
        return bool(result)

    def create_user_node(self, username: str) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (str)
        """
        query = f"g.addV('user').property('partitionKey', 'Answer').property('id', '{username}')"
        self.run_gremlin_query(query)

    def get_all_users(self) -> list:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """
        query = "g.V().hasLabel('user').id()"
        result = self.run_gremlin_query(query)
        return result

    def get_all_feedbacks(self) -> dict:
        """
        Return all feedbacks from all users in the database
            Return :
                - all_feedbacks : dict of all feedbacks
                    Dict {
                            username: [feedback1, feedback2, ...]
                    }
        """
        all_users = self.get_all_users()
        all_feedbacks = {}
        for user in all_users:
            all_feedbacks[user] = self.get_user_feedbacks(user)
        return all_feedbacks

    def get_user_feedbacks(self, username: str) -> list:
        """
        Return all feedbacks from a user in the database
            Return :
                - result : list of all feedbacks from a user (list of str)
        """
        query = f"g.V('{username}').outE().hasLabel('Feedback').values('text')"
        result = self.run_gremlin_query(query)
        return result

    def save_feedback(self, username: str, feedback: str) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        if not self.check_feedback_exist(username):
            self.create_feedback_node(username)
        self.create_feedback_edge(username, feedback)

    def check_feedback_exist(self, username: str) -> bool:
        """
        Check if a feedback exist in the database

        Parameters :
            - username : the username of the user (str)

        Return :
            - bool : True if the feedback exist, False otherwise
        """
        return self.check_node_exist(f"feedback{username}")

    def create_feedback_node(self, username: str) -> None:
        """
        Create a feedback node in the database

        Parameters :
            - username : the username of the user (str)
        """
        query = f"g.addV('Feedback').property('partitionKey', 'Feedback').property('id', 'feedback{username}')"
        self.run_gremlin_query(query)
        time.sleep(0.2)

    def create_feedback_edge(self, username: str, feedback: str) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        nb_feedback = self.get_nb_feedback_from_user(username)
        feedback_edge_id = f"Feedback-{username}-{nb_feedback+1}"
        self.run_gremlin_query(
            f"g.V('{username}').addE('Feedback').to(g.V('feedback{username}')).property('id', '{feedback_edge_id}').property('text', '{feedback}')"
        )

    def get_nb_feedback_from_user(self, username: str) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (str)

        Return :
            - result[0] : the number of feedbacks from a user (int)
        """
        query = f"g.V('{username}').outE().hasLabel('Feedback').count()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_nb_selected_edge(self) -> dict:
        """
        Return a dict with number of selected edge for each proposition

        Return :
            - nb_selected_edge : dict of number of selected edge for each proposition
                Dict{ edge_id: [text, nb_selected]}
        """
        query = "g.E().hasLabel('Answer').valueMap()"
        result = self.run_gremlin_query(query)

        nb_selected_edge = {}
        for edge in result:
            if "proposition_id" in edge:
                if edge["proposition_id"] not in nb_selected_edge:
                    nb_selected_edge[edge["proposition_id"]] = [edge["answer"], 0]
                nb_selected_edge[edge["proposition_id"]][1] += 1
        return nb_selected_edge

    def check_form_exist(self, username: str, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """
        return self.check_node_exist(f"{username}-answer1-{form_name}")

    def get_weight(self, edge_id: str) -> list:
        """
        Get the list_coef from the edge with edge_id id

        Parameters:
            - edge_id (str): id of the edge in the db

        Return:
            - list_weight (list(float)): list of the weights of the edge
        """
        list_weight = self.run_gremlin_query(f"g.E('{edge_id}').properties('list_coef').value()")[0].split(", ")
        for i_weight, weight in enumerate(list_weight):
            list_weight[i_weight] = float(weight)
        return list_weight

    def calcul_best_ais(self, nb_ai: int, answers: list) -> list:
        """
        Calculate the best AI to use for the user

        Parameters:
            - nb_ai (int): number of AI to return
            - answers (list): list of the answers of the user

        Return:
            - list_bests_ais (list): list of the best AI to use
        """
        list_ai = self.run_gremlin_query("g.V('1').properties('list_AI')")[0]["value"].split(", ")
        edges_id = self.get_edges_id(answers)
        coef_ai = np.array([1] * len(list_ai))
        for edge_id in edges_id:
            list_coef = self.get_weight(edge_id)
            coef_ai = np.multiply(coef_ai, list_coef)
        # we put all NaN value to -1
        for i_coef, coef in enumerate(coef_ai):
            if coef != coef:
                coef_ai[i_coef] = -1
        best = list(heapq.nlargest(nb_ai, np.array(coef_ai)))
        # we put the best nb_ai in list_bests_ais
        list_bests_ais = []
        for i_ai in _range(nb_ai):
            if best[i_ai] > 0:
                index = list(coef_ai).index(best[i_ai])
                list_bests_ais.append(list_ai[index])
        return list_bests_ais

    def get_edges_id(self, answers: list) -> list:
        """
        Get the edges id of the answers

        Parameters:
            - answers (list): list of the answers of the user

        Return:
            - edges_id (list): list of the edges id of the answers of the user
        """
        edges_id = []
        for i_question, question_id in enumerate(self.list_questions_id):
            label = self.get_question_label(question_id)
            if label == "Q_Open":
                edges_id.append(self.run_gremlin_query(f"g.V('{question_id}').outE().id()")[0])
            else:
                for answer in answers[i_question]:
                    edges_id.append(
                        self.run_gremlin_query(f"g.V('{question_id}').outE().has('text', '{answer}').id()")[0]
                    )

        return edges_id

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
        if not self.check_user_exist(username):
            self.create_user_node(username)
        if self.check_form_exist(username, form_name):
            return False

        self.list_questions_id.append("end")
        i = 0
        while self.list_questions_id[i] != "end":
            new_node_name = f"{username}-answer{self.list_questions_id[i]}-{form_name}"
            if not self.check_node_exist(new_node_name):
                self.create_answer_node(self.list_questions_id[i], new_node_name)
            next_new_node_name = f"{username}-answer{self.list_questions_id[i+1]}-{form_name}"
            if not self.check_node_exist(next_new_node_name):
                self.create_answer_node(self.list_questions_id[i + 1], next_new_node_name)
            self.create_answer_edge(new_node_name, next_new_node_name, answers[i], self.list_questions_id[i])
            i += 1
        # link between the first node of answers and the user
        first_node_id = f"{username}-answer{self.list_questions_id[0]}-{form_name}"
        self.run_gremlin_query(
            "g.V('" + username + "').addE('Answer').to(g.V('" + first_node_id + "')).property('partitionKey', 'Answer')"
        )
        self.list_questions_id.remove("end")
        list_bests_ais = self.calcul_best_ais(5, answers)
        list_bests_ais_string = str(list_bests_ais)[1:-1]
        self.run_gremlin_query(
            "g.V('" + first_node_id + "').property('list_bests_AIs', '" + list_bests_ais_string + "')"
        )
        return True

    def create_answer_node(self, question_id: str, new_node_id: str) -> None:
        """
        Create a question node in the database

        Parameters:
            - question_id (str): id of the question
            - new_node_id (str): id of the new node
        """
        if "end" in new_node_id:
            self.run_gremlin_query(
                f"g.addV('end').property('partitionKey', 'Answer').property('id', '{new_node_id}').property('question_id', '{question_id}')"
            )
        else:
            question_text = self.get_question_text(question_id)
            self.run_gremlin_query(
                f"g.addV('Answer').property('partitionKey', 'Answer').property('id', '{new_node_id}').property('question', '{question_text}').property('question_id', '{question_id}')"
            )

    def create_answer_edge(self, source_node_id: str, target_node_id: str, answers: list, question_id: str):
        """
        Create an edge between two nodes

        Parameters:
            - source_node_id (str): id of the source node
            - target_node_id (str): id of the target node
            - answers (list): list of the answers of the user
            - question_id (str): id of the question form
        """
        time.sleep(0.05)
        for answer in answers:
            self.run_gremlin_query(
                f"g.V('{source_node_id}').addE('Answer').to(g.V('{target_node_id}')).property('answer', '{answer}').property('proposition_id', '{self.get_proposition_id(question_id, answer)}')"
            )

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
        # We first delete the existing graph
        node_id = username + "-answer1-" + str(form_name)
        end = True
        while end:
            next_node_id = self.run_gremlin_query("g.V('" + node_id + "').out().properties('id')")
            # we delete the node
            self.run_gremlin_query("g.V('" + node_id + "').drop()")
            if not next_node_id:
                end = False
            else:
                node_id = next_node_id[0]["value"]
        return self.save_answers(username, new_form_name, answers)

    def get_proposition_id(self, source_node_id: str, answer: str) -> str:
        """
        Get the id of a proposition

        Parameters:
            - source_node_id (str): id of the source node
            - answer (str): answer of the user

        Return:
            - str: id of the proposition
        """
        nb_edges = self.run_gremlin_query(f"g.V('{source_node_id}').outE().count()")[0]
        if nb_edges == 1:
            return self.run_gremlin_query(f"g.V('{source_node_id}').outE().id()")[0]
        else:
            return self.run_gremlin_query(f"g.V('{source_node_id}').outE().has('text', '{answer}').id()")[0]

    def get_all_forms(self, username: str) -> list:
        """
        Get all the forms of a user

        Parameters:
            - username (str): username of the user

        Return:
            - list: list of the forms_id
        """
        return self.run_gremlin_query(f"g.V('{username}').outE().hasLabel('Answer').inV().id()")

    def get_list_answers(self, selected_form: str) -> list:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list: list of the answers
        """
        answers = []
        node = selected_form
        node_label = self.get_question_label(node)
        while node_label != "end":
            answer = self.run_gremlin_query(f"g.V('{node}').outE().properties('answer').value()")
            answers.append(answer)
            node = self.run_gremlin_query(f"g.V('{node}').outE().inV().id()")[0]
            node_label = self.get_question_label(node)
        return answers


def main():
    database = DbConnection()
    database.make_connection()
    database.get_one_question([])
    database.get_one_question([["oui"]])
    database.get_one_question([["oui"], ["Yes"]])
    database.get_one_question([["oui"], ["Yes"], ["DataSet, CSV or Data Base"]])
    database.get_one_question([["oui"], ["Yes"], ["DataSet, CSV or Data Base"], ["Predict a numerical value"]])

    database.get_one_question(
        [
            ["oui"],
            ["Yes"],
            ["DataSet, CSV or Data Base"],
            ["Predict a numerical value"],
            ["Minimize the average error. "],
        ]
    )

    database.get_one_question(
        [
            ["oui"],
            ["Yes"],
            ["DataSet, CSV or Data Base"],
            ["Predict a numerical value"],
            ["Minimize the average error. "],
            ["Higher speed"],
        ]
    )

    database.get_one_question(
        [
            ["oui"],
            ["Yes"],
            ["DataSet, CSV or Data Base"],
            ["Predict a numerical value"],
            ["Minimize the average error. "],
            ["Higher speed"],
            ["No"],
        ]
    )

    database.get_one_question(
        [
            ["oui"],
            ["Yes"],
            ["DataSet, CSV or Data Base"],
            ["Predict a numerical value"],
            ["Minimize the average error. "],
            ["Higher speed"],
            ["No"],
            ["Internal User"],
        ]
    )
    database.get_one_question(
        [
            ["oui"],
            ["Yes"],
            ["DataSet, CSV or Data Base"],
            ["Predict a numerical value"],
            ["Minimize the average error. "],
            ["Higher speed"],
            ["No"],
            ["Internal User"],
            ["Diagram"],
        ]
    )
    print(
        database.get_edges_id(
            [
                ["oui"],
                ["Yes"],
                ["DataSet, CSV or Data Base"],
                ["Predict a numerical value"],
                ["Minimize the average error. "],
                ["Higher speed"],
                ["No"],
                ["Internal User"],
                ["Diagram", "Tables"],
            ]
        )
    )
    print(database.get_proposition_id("2", "Yes"))
    print(database.get_list_answers("Canary-answer1-Test2"))
    database.close()


if __name__ == "__main__":
    main()
