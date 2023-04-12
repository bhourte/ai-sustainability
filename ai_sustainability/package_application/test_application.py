"""
File with our Application class
"""
from ai_sustainability.package_data_access.db_connection import DbConnection
from ai_sustainability.utils.models import (
    AnswersList,
    Feedback,
    Proposition,
    Question,
    SelectedEdge,
    User,
    UserFeedback,
)


class Application:
    """
    Class used to make the link between the database and the UI
    """

    database: DbConnection

    def __init__(self) -> None:
        self.list_questions: list[Question] = []
        self.modif_crypted = False
        self.create_list_questions()

    def create_list_questions(self) -> None:
        answer1 = Proposition(
            proposition_id="1", text="Answer1", help_text="Answer1", modif_crypted=False, list_coef=[]
        )
        answer2 = Proposition(
            proposition_id="2", text="Answer2", help_text="Answer2", modif_crypted=False, list_coef=[]
        )
        Q1 = Question(question_id="1", text="Q1", type="Q_QCM", help_text="1", answers=[answer1, answer2])
        Q2 = Question(question_id="2", text="Q2", type="Q_QCM", help_text="2", answers=[answer1, answer2])
        Q3 = Question(question_id="3", text="Q3", type="Q_QCM", help_text="3", answers=[answer1, answer2])
        Q4 = Question(question_id="4", text="Q4", type="Q_QCM", help_text="4", answers=[answer1, answer2])
        Q5 = Question(question_id="5", text="Q5", type="Q_QCM", help_text="5", answers=[answer1, answer2])
        Q6 = Question(question_id="6", text="", type="end", help_text="", answers=[])
        self.questions = [Q1, Q2, Q3, Q4, Q5, Q6]

    def get_next_question(self, answer_list: AnswersList) -> Question:
        """
        Get the id of the next question

        Parameters :
            - answer : the answer given by the user for the question (if "" : this means no specific answer eg: Q_Next)

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """
        self.list_questions = self.list_questions[: len(answer_list)]
        return self.questions[len(answer_list)]

    def check_form_exist(self, username: User, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """
        return True

    def calcul_best_ais(self, nb_ai: int, answers: AnswersList) -> list[str]:
        """
        Calculate the name best AI to use for the user

        Parameters:
            - nb_ai (int): number of AI to return
            - answers (list): list of the answers of the user

        Return:
            - list_bests_ais (list): list of the best AI to use
        """
        return [""]

    def save_answers(self, username: User, form_name: str, answers: AnswersList) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user

        Return:
            - bool: True if the answers are saved, False if the form already exist
        """
        return True

    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (str): username of the user

        Return:
            - list of the forms_id
        """
        return [""]

    def get_list_answers(self, selected_form: str) -> AnswersList:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list of the answers
        """
        return AnswersList([])

    def get_all_users(self) -> list[User]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """
        return []

    def check_user_exist(self, username: User) -> bool:
        """
        Check if a user exists in the database

        Parameters :
            - username : the username of the user (str)
        """
        return True

    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """
        return []

    def get_nb_selected_edge_stats(self) -> list[SelectedEdge]:
        """
        Return a dict with number of selected edge for each proposition
        Especially for stats showing
        Return :
            - list of SelectedEdge
        """
        return []
