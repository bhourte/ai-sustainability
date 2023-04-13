"""
File with our Application class
"""
from ai_sustainability.package_business.business import Business
from ai_sustainability.package_data_access.db_connection import DbConnection
from ai_sustainability.utils.models import (
    AnswersList,
    Feedback,
    Question,
    SelectedEdge,
    User,
    UserFeedback,
)


class Application:
    """
    Class used to make the link between the database and the UI
    """

    def __init__(self) -> None:
        self.database = DbConnection()
        self.business = Business()
        self.list_questions: list[Question] = []
        self.modif_crypted = False

    def get_next_question(self, answer_list: AnswersList) -> Question:
        """
        Get the id of the next question

        Parameters :
            - answer : the answer given by the user for the question (if "" : this means no specific answer eg: Q_Next)

        Return :
            - a Question corresponding to the next question according to the actual_question and answer provided
        """
        if len(answer_list) < len(self.list_questions):
            self.list_questions = self.list_questions[: len(answer_list)]
        if not answer_list:  # The form is empty, so we create a question 0 to initialise it
            start = Question(question_id="0", text="", type="start", help_text="", answers=[])
            self.list_questions.append(self.database.get_next_question(start, []))
            return self.list_questions[-1]

        actual_question = self.list_questions[-1]
        if len(answer_list) > 1 and answer_list[1][0].text == "Yes":
            self.modif_crypted = True
        next_question = self.database.get_next_question(actual_question, answer_list[-1])
        if self.modif_crypted:
            list_proposition = []
            for i in next_question.answers:
                if not i.modif_crypted:
                    list_proposition.append(i)
            next_question.answers = list_proposition
        self.list_questions.append(next_question)
        return next_question

    def calcul_best_ais(self, nb_ai: int, answers: AnswersList) -> list[str]:
        """
        Calculate the name best AI to use for the user

        Parameters:
            - nb_ai (int): number of AI to return
            - answers (list): list of the answers of the user

        Return:
            - list_bests_ais (list): list of the best AI to use
        """
        list_ai = self.database.get_all_ais()
        return self.business.calcul_best_ais(nb_ai=nb_ai, list_ai=list_ai, list_answers=answers)

    def get_best_ais(self, username: User, form_name: str) -> list[str]:
        """
        Method used to retreive all the N_best Ais stored in a answer
        """
        return self.database.get_best_ais(username, form_name)

    def save_answers(self, username: User, form_name: str, answers: AnswersList, list_best_ai: list[str]) -> bool:
        """
        Save the answers of a user in the database

        Parameters:
            - username (str): username of the user
            - form_name (str): name of the form
            - answers (list): list of the answers of the user

        Return:
            - bool: True if the answers are saved, False if the form already exist
        """
        return self.database.save_answers(username, form_name, answers, self.list_questions, list_best_ai)

    def change_answers(
        self, answers: AnswersList, username: User, form_name: str, new_form_name: str, list_best_ai: list[str]
    ) -> bool:
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
        return self.database.change_answers(
            answers, username, form_name, new_form_name, self.list_questions, list_best_ai
        )

    def get_all_users(self) -> list[User]:
        """
        Return all users in the database
            Return :
                - result : list of all users (list of str)
        """
        return self.database.get_all_users()

    def get_all_forms_names(self, username: User) -> list[str]:
        """
        Get all names of the forms of a user (in fact, get all the id lol)

        Parameters:
            - username (str): username of the user

        Return:
            - list of the forms_id
        """
        return self.database.get_all_forms_names(username)

    def get_list_answers(self, username: User, selected_form: str) -> AnswersList:
        """
        Get the list of answers of a form

        Parameters:
            - selected_form (str): id of the form

        Return:
            - list of the answers
        """
        return self.database.get_list_answers(username, selected_form)

    def get_all_feedbacks(self) -> list[UserFeedback]:
        """
        Return all feedbacks from all users in the database
        """
        return self.database.get_all_feedbacks()

    def check_user_exist(self, username: User) -> bool:
        """
        Check if a user exists in the database

        Parameters :
            - username : the username of the user (str)
        """
        return self.database.check_node_exist(username)

    def check_form_exist(self, username: User, form_name: str) -> bool:
        """
        Check if a form exist in the database

        Parameters :
            - username : the username of the user (str)
            - form_name : the name of the form (str)

        Return :
            - bool : True if the form exist, False otherwise
        """
        return self.database.check_node_exist(f"{username}-answer1-{form_name}")

    def save_feedback(self, username: User, feedback: Feedback) -> None:
        """
        Save a feedback from a user in the database

        Parameters :
            - username : the username of the user (str)
            - feedback : the feedback given by the user (str)
        """
        self.database.save_feedback(username, feedback)

    def get_nb_selected_edge_stats(self) -> list[SelectedEdge]:
        """
        Return a dict with number of selected edge for each proposition
        Especially for stats showing
        Return :
            - list of SelectedEdge
        """
        print(self.database.get_nb_selected_edge())
        return []
