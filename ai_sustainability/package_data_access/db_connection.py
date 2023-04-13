"""
This file contains the class DbConnection, used to connect to the database and to run the queries
"""
import time

from decouple import config
from gremlin_python import statics
from gremlin_python.driver import client, serializer

from ai_sustainability.package_data_access.db_interface import DBInterface
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

FIRST_NODE_ID = "1"
_map = map
statics.load_statics(globals())


def connect(endpoint: str, database_name: str, container_name: str, primary_key: str) -> client.Client:
    return client.Client(
        "wss://" + endpoint + ":443/",
        "g",
        username="/dbs/" + database_name + "/colls/" + container_name,
        password=primary_key,
        message_serializer=serializer.GraphSONSerializersV2d0(),
    )


class DbConnection(DBInterface):
    def __init__(self) -> None:
        self.gremlin_client: client.Client = connect(
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

    ########## Useful method ##########

    def run_gremlin_query(self, query: Query) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (string) (Exemple : "g.V()")

        Return :
            - list of all result that correspond to the query (list)
        """
        run = self.gremlin_client.submit(query).all()
        return run.result()

    def get_next_question(self, actual_question: Question, answer: UserAnswers) -> Question:
        """
        Get the id of the next question

        Parameters :
            - actual_question : the actual Question
            - answer : the answer given by the user for the question (if "" : this means no specific answer eg: Q_Next)

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """
        if actual_question.type in ("Q_Open", "Q_QRM"):
            query = Query(f"g.V('{actual_question.question_id}').out()")
        elif actual_question.type in ("Q_QCM", "Q_QCM_Bool"):
            query = Query(f"g.V('{actual_question.question_id}').outE().has('text','{answer[0].text}').inV()")
        elif actual_question.type == "start":
            query = Query(f"g.V('{FIRST_NODE_ID}')")
        elif actual_question.type == "end":
            return Question("end", "end", [], "end", "end")
        else:
            raise ValueError(f"Question type {actual_question.type} not supported")
        next_question = self.run_gremlin_query(query)[0]
        return Question(
            question_id=next_question["id"],
            text=next_question["properties"]["text"][0]["value"] if "text" in next_question["properties"] else "",
            answers=self.get_propositions(next_question["id"]),
            help_text=next_question["properties"]["help text"][0]["value"]
            if "help text" in next_question["properties"]
            else "",
            type=next_question["label"],
        )

    def get_propositions(self, question_id: str) -> list[Proposition]:
        """
        Get the propositions of a question

        Parameters :
            - question_id : the id of the question

        Return :
            - a list of propositions (list of Proposition)
        """
        query = Query(f"g.V('{question_id}').outE()")
        props = self.run_gremlin_query(query)
        propositions = []
        for prop in props:
            propositions.append(
                Proposition(
                    proposition_id=prop["id"],
                    text=prop["properties"]["text"] if "text" in prop["properties"] else "",
                    help_text=prop["properties"]["help text"] if "help text" in prop["properties"] else "",
                    modif_crypted=prop["properties"]["modif_crypted"] == "true"
                    if "modif_crypted" in prop["properties"]
                    else False,
                    list_coef=[float(coef) for coef in (prop["properties"]["list_coef"].split(", "))]
                    if "list_coef" in prop["properties"]
                    else [],
                )
            )
        return propositions

    # # TODO : check if this method is still used
    # def get_node(self, node_id: str) -> dict:
    #     """
    #     Check if a node exists in the database

    #     Parameters :
    #         - node_id : the id of the node (str)

    #     Return :
    #         - a dict containing all information of the node
    #     """
    #     query = Query(f"g.V('{node_id}')")
    #     return self.run_gremlin_query(query)[0]

    def create_user_node(self, username: User) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (str)
        """
        query = Query(f"g.addV('user').property('partitionKey', 'Answer').property('id', '{username}')")
        self.run_gremlin_query(query)

    def get_all_users(self) -> list[User]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """
        query = Query("g.V().hasLabel('user').id()")
        return self.run_gremlin_query(query)

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """
        all_users = self.get_all_users()
        all_feedbacks = []
        for user in all_users:
            all_feedbacks.append(self.get_user_feedbacks(user))
        return all_feedbacks

    def get_user_feedbacks(self, username: User) -> UserFeedback:
        """
        Return all feedbacks from a user in the database
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').values('text')")
        return UserFeedback(username, self.run_gremlin_query(query))

    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        if not self.check_feedback_exist(username):
            self.create_feedback_node(username)
        self.create_feedback_edge(username, feedback)

    def check_feedback_exist(self, username: User) -> bool:
        """
        Check if a feedback exist in the database

        Parameters :
            - username : the username of the user (str)

        Return :
            - bool : True if the feedback exist, False otherwise
        """
        return self.check_node_exist(f"feedback{username}")

    def check_node_exist(self, node_id: str) -> bool:
        """
        Check if a node exists in the database

        Parameters :
            - node_id : the id of the node (str)
        """
        query = Query(f"g.V('{node_id}')")
        return bool(self.run_gremlin_query(query))

    def create_feedback_node(self, username: User) -> None:
        """
        Create a feedback node in the database

        Parameters :
            - username : the username of the user (str)
        """
        query = Query(f"g.addV('Feedback').property('partitionKey', 'Feedback').property('id', 'feedback{username}')")
        self.run_gremlin_query(query)
        time.sleep(0.2)  # used to wait the node creation before calling the edge creation

    def create_feedback_edge(self, username: User, feedback: Feedback) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        nb_feedback = self.get_nb_feedback_from_user(username)
        feedback_edge_id = f"Feedback-{username}-{nb_feedback+1}"
        self.run_gremlin_query(
            Query(
                f"g.V('{username}').addE('Feedback').to(g.V('feedback{username}')).property('id', '{feedback_edge_id}').property('text', '{feedback}')"
            )
        )

    def get_nb_feedback_from_user(self, username: User) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (str)

        Return :
            - the number of feedbacks from a user (int)
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').count()")
        return self.run_gremlin_query(query)[0]

    def get_weight(self, edge_id: str) -> list[float]:
        """
        Get the list_coef from the edge with edge_id id

        Parameters:
            - edge_id (str): id of the edge in the db

        Return:
            - list of the weights of the edge
        """
        list_weight = self.run_gremlin_query(Query(f"g.E('{edge_id}').properties('list_coef').value()"))[0].split(", ")
        for i_weight, weight in enumerate(list_weight):
            list_weight[i_weight] = float(weight)
        return list_weight

    def save_answers(
        self, username: User, form_name: str, answers: AnswersList, questions: list[Question], best_ais: list[str]
    ) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user

        Return:
            - True if the answers are saved, False if the form already exist
        """
        if not self.check_node_exist(username):
            self.create_user_node(username)
        if self.check_form_exist(username, form_name):
            return False
        i = 0
        while questions[i].type != "end":
            new_node_name = f"{username}-answer{questions[i].question_id}-{form_name}"
            if not self.check_node_exist(new_node_name):
                self.create_answer_node(questions[i], new_node_name)
            next_new_node_name = f"{username}-answer{questions[i+1].question_id}-{form_name}"
            if not self.check_node_exist(next_new_node_name):
                self.create_answer_node(questions[i + 1], next_new_node_name)
            self.create_answer_edges(new_node_name, next_new_node_name, answers[i])
            i += 1
        # link between the User node and the first answer node
        first_node_id = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        self.run_gremlin_query(Query(f"g.V('{first_node_id}).property('best_ais', '{best_ais[1:-1]}')"))
        self.run_gremlin_query(
            Query(f"g.V('{username}').addE('Answer').to(g.V('{first_node_id}')).property('partitionKey', 'Answer')")
        )
        return True

    def check_form_exist(self, username: str, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """
        return self.check_node_exist(f"{username}-answer{FIRST_NODE_ID}-{form_name}")

    def create_answer_node(self, question: Question, new_node_id: str) -> None:
        """
        Create a question node in the database

        Parameters:
            - question_id (str): id of the question
            - new_node_id (str): id of the new node
        """
        if question.type == "end":
            self.run_gremlin_query(
                Query(
                    f"g.addV('end').property('partitionKey', 'Answer').property('id', '{new_node_id}').property('question_id', '{question.question_id}')"
                )
            )
        else:
            self.run_gremlin_query(
                Query(
                    f"g.addV('Answer').property('partitionKey', 'Answer').property('id', '{new_node_id}').property('question', '{question.text}').property('question_id', '{question.question_id}')"
                )
            )

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
        time.sleep(0.05)  # we wait to be sure that the 2 nodes are well created
        for proposition in answers:
            self.run_gremlin_query(
                Query(
                    f"g.V('{source_node_id}').addE('Answer').to(g.V('{target_node_id}')).property('answer', '{proposition.text}').property('proposition_id', '{proposition.proposition_id}')"
                )
            )

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
        node_id = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        keep_going = True
        while keep_going:
            next_node_id = self.run_gremlin_query(Query(f"g.V('{node_id}').out().properties('id')"))
            self.run_gremlin_query(Query(f"g.V('{node_id}').drop()"))
            if not next_node_id:
                keep_going = False
            else:
                node_id = next_node_id[0]["value"]
        return self.save_answers(username, new_form_name, answers, questions, best_ais)

    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (str): username of the user

        Return:
            - list of the forms_id
        """
        forms_id = self.run_gremlin_query(Query(f"g.V('{username}').outE().hasLabel('Answer').inV().id()"))
        return list(_map(lambda x: x.split("-")[-1], forms_id))

    def get_list_answers(self, username: User, form_name: str) -> AnswersList:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list of the answers
        """
        list_answers = AnswersList()
        node = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        node_label = self.get_node_label(node)
        while node_label != "end":
            list_answers.append(self.get_answers(node))
            node = self.run_gremlin_query(Query(f"g.V('{node}').outE().inV().id()"))[0]
            node_label = self.get_node_label(node)
        return list_answers

    def get_answers(self, node_id: str) -> list[Proposition]:
        query = Query(f"g.V('{node_id}').outE()")
        props = self.run_gremlin_query(query)
        propositions = []
        for prop in props:
            propositions.append(
                Proposition(
                    proposition_id=prop["properties"]["proposition_id"],
                    text=prop["properties"]["answer"] if "answer" in prop["properties"] else "",
                    help_text="",
                    modif_crypted=False,
                    list_coef=prop["properties"]["list_coef"] if "list_coef" in prop["properties"] else [],
                )
            )
        return propositions

    def get_node_label(self, node_id: str) -> str:
        return self.run_gremlin_query(Query(f"g.V('{node_id}').label()"))[0]

    ########## Less useful method ##########  TODO : see if we keep them
    def get_nb_selected_edge(self) -> list[SelectedEdge]:
        """
        Return a dict with number of selected edge for each proposition

        Return :
            - number of selected edge for each proposition
        """
        query = Query("g.E().hasLabel('Answer').valueMap()")
        result = self.run_gremlin_query(query)

        nb_selected_edge = {}
        for edge in result:
            if "proposition_id" in edge:
                if edge["proposition_id"] not in nb_selected_edge:
                    nb_selected_edge[edge["proposition_id"]] = [edge["answer"], 0]
                nb_selected_edge[edge["proposition_id"]][1] += 1

        selected_edges = []
        for key, val in nb_selected_edge.items():
            selected_edges.append(SelectedEdge(key, val[0], val[1]))
        return selected_edges

    def get_all_ais(self) -> list[str]:
        """
        Get all the ais in the db

        Return:
            - list of the ais
        """
        return self.run_gremlin_query(Query(f"g.V('{FIRST_NODE_ID}').properties('list_AI').value()"))[0].split(", ")

    def get_best_ais(self, username: User, form_name: str):
        """
        Return the best ais for a form
        """
        form_id = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        query = Query(f"g.V('{form_id}').properties('list_AI').value()")
        return self.run_gremlin_query(query)[0].split(", ")
