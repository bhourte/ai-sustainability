"""
This file contains the class DbConnection, used to connect to the database and to run the queries
"""
import time
from hmac import new

from decouple import config
from gremlin_python import statics
from gremlin_python.driver import client, serializer

from ai_sustainability.package_business.models import (
    Answer,
    AnswersList,
    AnswersStats,
    Feedback,
    Form,
    Query,
    Question,
    UserFeedback,
    Username,
)
from ai_sustainability.package_data_access.db_interface import DBInterface

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
    """
    Class to manage the database Gremlin CosmosDB
    """

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

    def run_gremlin_query(self, query: Query) -> list:
        """
        Run a gremlin query

        Parameters :
            - query : the gremlin query to run (Query) (Exemple : Query("g.V()"))

        Return :
            - list of all result that correspond to the query (list)
        """
        run = self.gremlin_client.submit(query).all()
        return run.result()

    def get_next_question(self, form: Form, question_number: int) -> Question:
        """
        get the next question

        Parameters :
            - actual_question : the actual Question (Question)
            - answer : the answer given by the user for the question (UserAnswers)

        Return :
            - a Question corresponding to the next question according to
                the actual_question and answer provided (Question)
        """
        if form.already_completed and len(form.question_list) > question_number:
            return form.question_list[question_number]
        actual_question = None if not form.question_list else form.question_list[question_number - 1]
        if actual_question is None:
            query = Query(f"g.V('{FIRST_NODE_ID}')")
        elif actual_question.type in ("Q_Open", "Q_QRM"):
            query = Query(f"g.V('{actual_question.question_id}').out()")
        elif actual_question.type in ("Q_QCM", "Q_QCM_Bool"):
            query = Query(
                f"g.V('{actual_question.question_id}').outE().has('text','{actual_question.answers_choosen[0].text}').inV()"
            )
        elif actual_question.type == "end":
            return form.question_list[-1]
        else:
            raise ValueError(f"Question type {actual_question.type} not supported")
        next_question = self.run_gremlin_query(query)[0]
        new_question = Question(
            question_id=next_question["id"],
            text=next_question["properties"]["text"][0]["value"] if "text" in next_question["properties"] else "",
            help_text=next_question["properties"]["help text"][0]["value"]
            if "help text" in next_question["properties"]
            else "",
            answers=[],
            type=next_question["label"],
        )
        new_question.set_answers(self.get_propositions(next_question))
        form.add_question(new_question)
        return form.question_list[-1]

    def get_propositions(self, question: dict) -> list[Answer]:
        """
        Get the propositions for a question in the database

        Parameters :
            - question_id : the id of the question (str)

        Return :
            - propositions : list of all propositions for the question (list of Proposition)
        """
        query = Query(f"g.V('{question['id']}').outE()")
        props = self.run_gremlin_query(query)
        propositions = []
        for prop in props:
            propositions.append(
                Answer(
                    answer_id=prop["id"],
                    text=prop["properties"]["text"] if "text" in prop["properties"] else "Q_Next",
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

    def create_user_node(self, username: Username) -> None:
        """
        Create a user node in the database

        Parameters :
            - username : the username of the user (User)
        """
        query = Query(f"g.addV('user').property('partitionKey', 'Answer').property('id', '{username}')")
        self.run_gremlin_query(query)

    def get_all_users(self) -> list[Username]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of User)
        """
        query = Query("g.V().hasLabel('user').id()")
        return self.run_gremlin_query(query)

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks in the database

        Return :
            - result : list of all feedbacks (list of UserFeedback)
        """
        all_users = self.get_all_users()
        all_feedbacks = []
        for user in all_users:
            all_feedbacks.append(self.get_user_feedbacks(user))
        return all_feedbacks

    def get_user_feedbacks(self, username: Username) -> UserFeedback:
        """
        Return all feedbacks from a user in the database

        Parameters :
            - username : the username of the user (User)

        Return :
            - result : list of all feedbacks from the user (UserFeedback)
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').values('text')")
        return UserFeedback(username, self.run_gremlin_query(query))

    def save_feedback(self, username: Username, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (User)
            - feedback : the feedback given by the user (Feedback)
        """
        if not self.check_feedback_exist(username):
            self.create_feedback_node(username)
        self.create_feedback_edge(username, feedback)

    def check_feedback_exist(self, username: Username) -> bool:
        """
        Check if a feedback exist in the database

        Parameters :
            - username : the username of the user (User)

        Return :
            - bool : True if the feedback exist, False otherwise
        """
        return self.check_node_exist(f"feedback{username}")

    def check_node_exist(self, node_id: str) -> bool:
        """
        Check if a node exists in the database

        Parameters :
            - node_id : the id of the node (str)

        Return :
            - bool : True if the node exists, False otherwise
        """
        query = Query(f"g.V('{node_id}')")
        return bool(self.run_gremlin_query(query))

    def create_feedback_node(self, username: Username) -> None:
        """
        Create a feedback node in the database

        Parameters :
            - username : the username of the user (User)
        """
        query = Query(f"g.addV('Feedback').property('partitionKey', 'Feedback').property('id', 'feedback{username}')")
        self.run_gremlin_query(query)
        time.sleep(0.2)  # used to wait the node creation before calling the edge creation

    def create_feedback_edge(self, username: Username, feedback: Feedback) -> None:
        """
        Create a feedback edge in the database

        Parameters :
            - username : the username of the user (User)
            - feedback : the feedback given by the user (Feedback)
        """
        nb_feedback = self.get_nb_feedback_from_user(username)
        feedback_edge_id = f"Feedback-{username}-{nb_feedback+1}"
        self.run_gremlin_query(
            Query(
                f"g.V('{username}').addE('Feedback').to(g.V('feedback{username}')).property('id', '{feedback_edge_id}').property('text', '{feedback}')"
            )
        )

    def get_nb_feedback_from_user(self, username: Username) -> int:
        """
        Return the number of feedbacks from a user

        Parameters :
            - username : the username of the user (User)

        Return :
            - the number of feedbacks from a user (int)
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').count()")
        return self.run_gremlin_query(query)[0]

    def save_answers(self, form: Form, best_ais: list[str]) -> bool:
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
        if not self.check_node_exist(form.username):
            self.create_user_node(form.username)
        if self.check_form_exist(form.username, form.form_name):
            return False
        i = 0
        while form.question_list[i].type != "end":
            new_node_name = f"{form.username}-answer{form.question_list[i].question_id}-{form.form_name}"
            if not self.check_node_exist(new_node_name):
                self.create_answer_node(form.question_list[i], new_node_name)
            next_new_node_name = f"{form.username}-answer{form.question_list[i+1].question_id}-{form.form_name}"
            if not self.check_node_exist(next_new_node_name):
                self.create_answer_node(form.question_list[i + 1], next_new_node_name)
            self.create_answer_edges(new_node_name, next_new_node_name, form.question_list[i].answers_choosen)
            i += 1
        # link between the User node and the first answer node
        first_node_id = f"{form.username}-answer{FIRST_NODE_ID}-{form.form_name}"
        self.run_gremlin_query(Query(f"g.V('{first_node_id}').property('best_ais', '{str(best_ais)[1:-1]}')"))
        self.run_gremlin_query(
            Query(
                f"g.V('{form.username}').addE('Answer').to(g.V('{first_node_id}')).property('partitionKey', 'Answer')"
            )
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
            - question (Question): id of the question
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
        answers: AnswersList,
    ) -> None:
        """
        Create an edge between two nodes

        Parameters:
            - source_node_id (str): id of the source node
            - target_node_id (str): id of the target node
            - answers (UserAnswers): list of the answers of the user
        """
        time.sleep(0.05)  # we wait to be sure that the 2 nodes are well created
        for proposition in answers:
            self.run_gremlin_query(
                Query(
                    f"""
                        g.V('{source_node_id}')
                            .addE('Answer')
                            .to(g.V('{target_node_id}'))
                            .property('answer', '{proposition.text}')
                            .property('proposition_id', '{proposition.answer_id}')
                    """
                )
            )

    def update_answers(self, form: Form, new_form_name: str, best_ais: list[str]) -> bool:
        """
        Change the answer in db

        Parameters:
            - answers (AnswersList): list of answers
            - username (User): username of the user
            - form_name (str): name of the form
            - new_form_name (str): new name of the form
            - questions (list[Question]): list of the questions of the form
            - best_ais (list[str]): list of the best ais

        Return:
            - True if the answers are saved, False if the form already exist
        """
        node_id = f"{form.username}-answer{FIRST_NODE_ID}-{form.form_name}"
        keep_going = True
        while keep_going:
            next_node_id = self.run_gremlin_query(Query(f"g.V('{node_id}').out().properties('id')"))
            self.run_gremlin_query(Query(f"g.V('{node_id}').drop()"))
            if not next_node_id:
                keep_going = False
            else:
                node_id = next_node_id[0]["value"]
        form.set_name(new_form_name)
        return self.save_answers(form, best_ais)

    def get_all_forms_names(self, username: Username) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (User): username of the user

        Return:
            - list of the forms_id
        """
        forms_id = self.run_gremlin_query(Query(f"g.V('{username}').outE().hasLabel('Answer').inV().id()"))
        return list(_map(lambda x: x.split("-")[-1], forms_id))

    def get_previous_form(self, username: Username, selected_form_name: str) -> Form:
        form = Form()
        form.set_username(username)
        form.set_name(selected_form_name)
        form.already_completed = True
        node = f"{username}-answer{FIRST_NODE_ID}-{selected_form_name}"
        question_number = 0
        while self.get_node_label(node) != "end":
            self.get_next_question(form, question_number)
            answers = self.get_answers(node)
            form.add_previous_answers(answers)
            node = self.run_gremlin_query(Query(f"g.V('{node}').outE().inV().id()"))[0]
            question_number += 1
        self.get_next_question(form, question_number)
        return form

    def get_answers(self, node_id: str) -> list[Answer]:
        """
        Get the answers of a node (completed form)

        Parameters:
            - node_id (str): id of the node

        Return:
            - list of the answers (list[Answer])
        """
        query = Query(f"g.V('{node_id}').outE()")
        props = self.run_gremlin_query(query)
        answers = []
        for prop in props:
            answers.append(
                Answer(
                    answer_id=prop["properties"]["proposition_id"],
                    text=prop["properties"]["answer"] if "answer" in prop["properties"] else "",
                    help_text="",
                    modif_crypted=False,
                    list_coef=prop["properties"]["list_coef"] if "list_coef" in prop["properties"] else [],
                )
            )
        return answers

    def get_node_label(self, node_id: str) -> str:
        """
        Get the label of a node

        Parameters:
            - node_id (str): id of the node

        Return:
            - label of the node (str)
        """
        return self.run_gremlin_query(Query(f"g.V('{node_id}').label()"))[0]

    def get_nb_selected_edge(self) -> list[AnswersStats]:
        """
        Return a list of SelectedEdge with theb number of times edge was selected for each proposition

        Return :
            - selected_edges (list[SelectedEdge]) : list of SelectedEdge
        """
        query = Query("g.E().hasLabel('Answer').valueMap()")
        result = self.run_gremlin_query(query)

        nb_selected_edge: dict = {}  # key : proposition_id, value : [Answer dataclass, nb_selected]
        for edge in result:
            if "proposition_id" in edge:
                if edge["proposition_id"] not in nb_selected_edge:
                    query = Query(f"g.E('{edge['proposition_id']}')")
                    answer_dict = self.run_gremlin_query(query)[0]
                    text = "Q_Next" if "text" not in answer_dict["properties"] else answer_dict["properties"]["text"]
                    answer = Answer(answer_id=answer_dict["id"], text=text)
                    nb_selected_edge[edge["proposition_id"]] = [answer, 0]
                nb_selected_edge[edge["proposition_id"]][1] += 1

        selected_edges = []
        for _, val in nb_selected_edge.items():
            selected_edges.append((val[0], val[1]))
        return selected_edges

    def get_all_ais(self) -> list[str]:
        """
        Get all the ais in the db

        Return:
            - list of the ais (list[str])
        """
        return self.run_gremlin_query(Query(f"g.V('{FIRST_NODE_ID}').properties('list_AI').value()"))[0].split(", ")

    def get_best_ais(self, username: Username, form_name: str) -> list[str]:
        """
        Return the best ais for a form which was saved in the db

        Parameters:
            - username (User): username of the user
            - form_name (str): name of the form

        Return:
            - list of the best ais (list[str])
        """
        form_id = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        query = Query(f"g.V('{form_id}').properties('best_ais').value()")
        result = self.run_gremlin_query(query)
        return result[0].split(", ") if result[0] else []
