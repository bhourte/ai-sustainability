"""
This file contains the class DbConnection, used to connect to the database and to run the queries
"""
import time
from typing import Optional, Tuple

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
END_TYPE = config("END_TYPE")
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
            - query : the gremlin query to run (Exemple : Query("g.V()"))

        Return :
            - list of all result that correspond to the query
        """
        run = self.gremlin_client.submit(query).all()
        return run.result()

    def get_next_question(self, form: Form, question_number: int) -> Question:
        """
        get the next question according the form
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
                f"g.V('{actual_question.question_id}').outE().has('text','{actual_question.choosen_answers[0].text}').inV()"
            )
        elif actual_question.type == END_TYPE:
            return form.question_list[-1]
        else:
            raise ValueError(f"Question type {actual_question.type} not supported")
        next_question = self.run_gremlin_query(query)[0]
        new_question = Question(
            question_id=next_question["id"],
            text=next_question["properties"]["text"][0]["value"] if "text" in next_question["properties"] else "",
            type=next_question["label"],
        )
        new_question.help_text = (
            next_question["properties"]["help text"][0]["value"] if "help text" in next_question["properties"] else ""
        )
        new_question.possible_answers = self.get_propositions(new_question)
        form.add_question(new_question)
        return form.question_list[-1]

    def get_propositions(self, question: Question) -> list[Answer]:
        """
        Get all possibles Answers for a Question from the database
        """
        query = Query(f"g.V('{question.question_id}').outE()")
        existing_answers = self.run_gremlin_query(query)
        answers_list: list[Answer] = []
        for answer in existing_answers:
            answers_list.append(
                Answer(
                    answer_id=answer["id"],
                    text=answer["properties"]["text"] if "text" in answer["properties"] else "Q_Next",
                    help_text=answer["properties"]["help text"] if "help text" in answer["properties"] else "",
                    modif_crypted=answer["properties"]["modif_crypted"] == "true"
                    if "modif_crypted" in answer["properties"]
                    else False,
                    metric=None if "metric" not in answer["properties"] else answer["properties"]["metric"].split(","),
                    list_coef=[float(coef) for coef in (answer["properties"]["list_coef"].split(", "))]
                    if "list_coef" in answer["properties"]
                    else [],
                )
            )
        return answers_list

    def create_user_node(self, username: Optional[Username]) -> None:
        """
        Create a User node in the database
        """
        if username is None:
            return
        query = Query(f"g.addV('user').property('partitionKey', 'Answer').property('id', '{username}')")
        self.run_gremlin_query(query)

    def get_all_users(self) -> list[Username]:
        """
        Return all Username in the database
        """
        return self.run_gremlin_query(Query("g.V().hasLabel('user').id()"))

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all Feedbacks in the database
        """
        all_users = self.get_all_users()
        all_feedbacks = []
        for user in all_users:
            all_feedbacks.append(self.get_user_feedbacks(user))
        return all_feedbacks

    def get_user_feedbacks(self, username: Username) -> UserFeedback:
        """
        Return all feedbacks from a user in the database
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').values('text')")
        return UserFeedback(username, self.run_gremlin_query(query))

    def save_feedback(self, username: Username, feedback: Feedback) -> None:
        """
        Save a Feedback from a User in the database
        """
        if not self.check_feedback_exist(username):
            self.create_feedback_node(username)
        self.create_feedback_edge(username, feedback)

    def check_feedback_exist(self, username: Username) -> bool:
        """
        Check if a User has already give a Feedback
        """
        return self.check_node_exist(f"feedback{username}")

    def check_node_exist(self, node_id: Optional[str]) -> bool:
        """
        Check if a node exists in the database
        """
        if node_id is None or not node_id:
            return False
        query = Query(f"g.V('{node_id}')")
        return bool(self.run_gremlin_query(query))

    def create_feedback_node(self, username: Username) -> None:
        """
        Create a Feedback node in the database
        """
        query = Query(f"g.addV('Feedback').property('partitionKey', 'Feedback').property('id', 'feedback{username}')")
        self.run_gremlin_query(query)
        time.sleep(0.2)  # used to wait the node creation before calling the edge creation

    def create_feedback_edge(self, username: Username, feedback: Feedback) -> None:
        """
        Create a Feedback edge in the database
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
        Return the number of Feedbacks a User has give
        """
        query = Query(f"g.V('{username}').outE().hasLabel('Feedback').count()")
        return self.run_gremlin_query(query)[0]

    def save_answers(
        self, form: Form, best_ais: list[Tuple[str, float]], mlflow_id: Optional[str] = "", new_form_name: str = ""
    ) -> bool:
        """
        Save a Form completed by a User in the database, and drop the previous version of the Form if it's exist

        Return:
            - True if the answers are saved, False if the form already exist
        """
        if new_form_name:
            self.drop_form(form)
            form.form_name = new_form_name
        if not self.check_node_exist(form.username):
            self.create_user_node(form.username)
        if self.check_form_exist(form.username, form.form_name):
            return False
        i = 0
        while form.question_list[i].type != END_TYPE:
            new_node_name = f"{form.username}-answer{form.question_list[i].question_id}-{form.form_name}"
            if not self.check_node_exist(new_node_name):
                self.create_answer_node(form.question_list[i], new_node_name)
            next_new_node_name = f"{form.username}-answer{form.question_list[i+1].question_id}-{form.form_name}"
            if not self.check_node_exist(next_new_node_name):
                self.create_answer_node(form.question_list[i + 1], next_new_node_name)
            self.create_answer_edges(new_node_name, next_new_node_name, form.question_list[i].choosen_answers)
            i += 1
        # link between the User node and the first answer node
        first_node_id = f"{form.username}-answer{FIRST_NODE_ID}-{form.form_name}"
        string_best_ais = ", ".join([ai[0] for ai in best_ais])
        self.run_gremlin_query(Query(f"g.V('{first_node_id}').property('best_ais', '{str(string_best_ais)}')"))
        if mlflow_id is not None:
            self.run_gremlin_query(Query(f"g.V('{first_node_id}').property('mlflow_id', '{mlflow_id}')"))
        self.run_gremlin_query(
            Query(
                f"g.V('{form.username}').addE('Answer').to(g.V('{first_node_id}')).property('partitionKey', 'Answer')"
            )
        )
        return True

    def check_form_exist(self, username: Optional[Username], form_name: str) -> bool:
        """
        Check if a Form exist in the database
        """
        if username is None:
            return False
        return self.check_node_exist(f"{username}-answer{FIRST_NODE_ID}-{form_name}")

    def create_answer_node(self, question: Question, new_node_id: str) -> None:
        """
        Create a answered Question node in the database
        """
        if question.type == END_TYPE:
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
            - source_node_id : id of the source node
            - target_node_id : id of the target node
            - answers : list of the answers of the user
        """
        time.sleep(0.05)  # we wait to be sure that the previous nodes are well created
        for proposition in answers:
            query = f"""
                        g.V('{source_node_id}')
                            .addE('Answer')
                            .to(g.V('{target_node_id}'))
                            .property('answer', '{proposition.text}')
                            .property('proposition_id', '{proposition.answer_id}')
                            .property('list_coef', '{str(proposition.list_coef)[1:-1]}')
                    """
            if proposition.metric is not None:
                query += f""".property('metric', "{','.join(proposition.metric)}")"""
            self.run_gremlin_query(Query(query))

    def drop_form(self, form: Form) -> None:
        """
        drop a Form in the database
        """
        node_id = f"{form.username}-answer{FIRST_NODE_ID}-{form.form_name}"
        keep_going = True
        while keep_going:
            next_node_id = self.run_gremlin_query(Query(f"g.V('{node_id}').out().properties('id')"))
            self.run_gremlin_query(Query(f"g.V('{node_id}').drop()"))
            if not next_node_id:
                return
            node_id = next_node_id[0]["value"]

    def get_all_forms_names(self, username: Username) -> list[str]:
        """
        Get all names of the forms of a User
        """
        forms_id = self.run_gremlin_query(Query(f"g.V('{username}').outE().hasLabel('Answer').inV().id()"))
        return list(_map(lambda x: x.split("-")[-1], forms_id))

    def retrieve_previous_form(self, username: Username, selected_form_name: str) -> Form:
        """
        Retrieve a already answered Form from the database
        """
        form = Form()
        form.username = username
        form.form_name = selected_form_name
        form.already_completed = True
        node = f"{username}-answer{FIRST_NODE_ID}-{selected_form_name}"
        form.experiment_id = self.get_experiment(node)
        question_number = 0
        while self.get_node_label(node) != END_TYPE:
            self.get_next_question(form, question_number)
            answers = self.get_answers(node)
            form.last_question.choosen_answers = answers
            node = self.run_gremlin_query(Query(f"g.V('{node}').outE().inV().id()"))[0]
            question_number += 1
        self.get_next_question(form, question_number)
        return form

    def get_experiment(self, first_node: str) -> Optional[str]:
        """Retrieve the mlflow's experiment id of a previous completed form"""
        query = Query(f"g.V('{first_node}')")
        node = self.run_gremlin_query(query)[0]
        return node["properties"]["mlflow_id"][0]["value"] if "mlflow_id" in node["properties"] else None

    def get_answers(self, node_id: str) -> list[Answer]:
        """
        Get all Answers of a Question in a previous Form stord in the database
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
                    metric=prop["properties"]["metric"] if "metric" in prop["properties"] else None,
                    list_coef=[]
                    if "list_coef" not in prop["properties"] or not prop["properties"]["list_coef"]
                    else [float(coef) for coef in (prop["properties"]["list_coef"].split(", "))],
                )
            )
        return answers

    def get_node_label(self, node_id: str) -> str:
        """
        Get the label of a node
        """
        return self.run_gremlin_query(Query(f"g.V('{node_id}').label()"))[0]

    def get_nb_selected_edge(self) -> list[AnswersStats]:
        """
        Return a list of AnswersStats (Answer, nb_time_selected)
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
        Get all the ais existing in the db
        """
        return self.run_gremlin_query(Query(f"g.V('{FIRST_NODE_ID}').properties('list_AI').value()"))[0].split(", ")

    def get_best_ais(self, username: Username, form_name: str) -> list[str]:
        """
        Return the best ais for a form which was saved in the db
        """
        form_id = f"{username}-answer{FIRST_NODE_ID}-{form_name}"
        query = Query(f"g.V('{form_id}').properties('best_ais').value()")
        result = self.run_gremlin_query(query)
        return result[0].split(", ") if result[0] else []
