"""
Make the connection to the database, run the querys and close the connection

1)

    get_first_question() : get the first question of the form
    get_one_question() : 
        - get_question_text() : get the text of the question (str) with actual_question
        - get_answers_text() list of all the answers (str) with actual_question
        - get_help_text() : get the help text (str) with actual_question

        return : dict {
            1: text question
            2: list of answers
            3: help text
            4: Label question
        }
    save_answer() : save the answer in the database

    give answer(answer_list) : following the len of the list, we can find the question by the answer

    attributes :
        - list_questions (list) : list of past questions and last is actual_question (ids db)
    
    Methods :
    check_user_exist(username) : check if the user exist in the database
    save_feedback(feedback, username) : save the feedback in the database (feedback is a text)
    get_all_feedbacks() : get all the feedbacks in the database for all users
        Dict {
            username: [feedback1, feedback2, ...],
        }
    get_all_users() -> list(str)

"""

from decouple import config
from gremlin_python import statics
from gremlin_python.driver import client, serializer

statics.load_statics(globals())

FIRST_NODE_ID = "1"
LAST_NODE_ID = "9"


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
    def __init__(self):
        """
        Initialize the class with the connection to the database
        """
        self.gremlin_client = connect(
            endpoint="questions-db.gremlin.cosmos.azure.com",
            database_name="graphdb",
            container_name=config("DATABASENAME"),
            primary_key=config("PRIMARYKEY"),
        )
        self.list_questions_id = []

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
        """
        run = self.gremlin_client.submit(query).all()
        result = run.result()
        return result

    def get_one_question(self, answers) -> dict:
        """
        Get one question from the database

        Parameters :
            - answers : list of the answers given by the user (list of str)

        Return :
            - question : dict {
                1: question_text
                2: answers (list of str)
                3: help_text
                4: question_label
            }
        """
        question = {}
        self.truncate_questions(answers)
        question_id = self.get_next_question(answers)
        if question_id == LAST_NODE_ID:
            question["question_text"] = ""
            question["answers"] = []
            question["help_text"] = ""
            question["question_label"] = "end"
            return question
        self.list_questions_id.append(question_id)
        question["question_text"] = self.get_question_text(question_id)
        question["answers"] = self.get_answers_text(question_id)
        question["help_text"] = self.get_help_text(question_id)
        question["question_label"] = self.get_question_label(question_id)
        return question

    def get_question_text(self, question_id: str) -> str:
        query = f"g.V('{question_id}').properties('text').value()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_answers_text(self, question_id: str) -> list:
        query = f"g.V('{question_id}').outE().properties('text').value()"
        result = self.run_gremlin_query(query)
        return result

    def get_help_text(self, question_id: str) -> str:
        query = f"g.V('{question_id}').properties('help text').value()"
        help_text = self.run_gremlin_query(query)[0]
        query = f"g.V('{question_id}').outE().properties('help text').value()"
        answers_help_text = self.run_gremlin_query(query)
        answers_text = self.get_answers_text(question_id)
        for i, val in enumerate(answers_help_text):
            help_text += f"{answers_text[i]}: {val}"
        return help_text

    def get_question_label(self, question_id: str) -> str:
        query = f"g.V('{question_id}').label()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_next_question(self, answers: list) -> str:
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
        if len(answers) < len(self.list_questions_id):
            self.list_questions_id = self.list_questions_id[: len(answers)]

    def check_user_exist(self, username: str):
        return self.check_node_exist(username)

    def check_node_exist(self, node_id: str):
        query = f"g.V('{node_id}')"
        result = self.run_gremlin_query(query)
        return bool(result)

    def create_user(self, username: str):
        query = f"g.addV('user').property('partitionKey', 'Answer').property('id', '{username}')"
        self.run_gremlin_query(query)

    def get_all_users(self):
        query = "g.V().hasLabel('user').id()"
        result = self.run_gremlin_query(query)
        return result

    def get_all_feedbacks(self):
        """
        Return all feedbacks from all users in the database
            return : Dict {
                username: [feedback1, feedback2, ...]
            }
        """
        all_users = self.get_all_users()
        all_feedbacks = {}
        for user in all_users:
            all_feedbacks[user] = self.get_user_feedbacks(user)
        return all_feedbacks

    def get_user_feedbacks(self, username: str):
        """
        Return all feedbacks from a user in the database
            return : List of feedbacks
        """
        query = f"g.V('{username}').outE().hasLabel('Feedback').values('text')"
        result = self.run_gremlin_query(query)
        return result

    def save_feedback(self, username: str, feedback: str):
        """
        Save a feedback from a user in the database
        """
        if not self.check_feedback_exist(username):
            self.create_feedback_node(username)
        self.create_feedback_edge(username, feedback)

    def check_feedback_exist(self, username: str):
        """
        Check if a feedback exist in the database
        """
        return self.check_node_exist(f"feedback{username}")

    def create_feedback_node(self, username: str):
        """
        Create a feedback node in the database
        """
        query = f"g.addV('Feedback').property('partitionKey', 'Feedback').property('id', 'feedback{username}')"
        self.run_gremlin_query(query)

    def create_feedback_edge(self, username, feedback):
        nb_feedback = self.get_nb_feedback_from_user(username)
        feedback_edge_id = f"feedback{username}{nb_feedback}"
        self.run_gremlin_query(
            f"g.V('{username}').addE('Feedback').to(g.V('feedback{username}')).property('id', '{feedback_edge_id}').property('text', '{feedback}')"
        )

    def get_nb_feedback_from_user(self, username: str) -> int:
        """
        Return the number of feedbacks from a user
        """
        query = f"g.V('{username}').outE().hasLabel('Feedback').count()"
        result = self.run_gremlin_query(query)
        return result[0]

    def get_nb_selected_edge(self):
        """
        return : Dict{ edge_id: [text, nb_selected]}
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


def main():
    database = DbConnection()
    print(database.get_one_question([]))
    print(database.get_one_question([["oui"]]))
    print(database.get_one_question([["oui"], ["Yes"]]))
    print(database.get_one_question([["oui"], ["Yes"], ["DataSet, CSV or Data Base"]]))
    print(database.get_one_question([["oui"], ["Yes"], ["DataSet, CSV or Data Base"], ["Predict a numerical value"]]))
    print(
        database.get_one_question(
            [
                ["oui"],
                ["Yes"],
                ["DataSet, CSV or Data Base"],
                ["Predict a numerical value"],
                ["Minimize the average error. "],
            ]
        )
    )
    print(
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
    )
    print(
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
    )
    print(
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
    )
    print(
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
    )

    database.close()


if __name__ == "__main__":
    main()
