# TODO faire une nouvelle dataclass Form qui gere un formulaire
"""
File with all dataclass and Type we use in the form application

New models :
  NewType :
    - User
    - Query
    - Feedback
    - UserAnswers
    - AnswersList
  Dataclass :
    - Proposition
    - Question
    - UserFeedback
    - SelectedEdge
"""

import math
from dataclasses import dataclass, field
from typing import NewType

import numpy as np

Username = NewType("Username", str)
Query = NewType("Query", str)
Feedback = NewType("Feedback", str)


@dataclass(kw_only=True)
class Answer:
    """Dataclass corresponding to one proposition for a question (an edge in the database)"""

    answer_id: str
    text: str
    help_text: str = ""
    modif_crypted: bool = False
    list_coef: list[float] = field(default_factory=list)

    @property
    def question_in_id(self) -> str:
        return self.answer_id.split("-")[0]

    @property
    def question_out_id(self) -> str:
        return self.answer_id.split("-")[1]

    def __repr__(self) -> str:
        return f"Q{self.question_in_id} to Q{self.question_out_id}"


AnswersList = list[Answer]  # List of answers selected by the user in QuestionAnswer propositions
FormAnswers = list[AnswersList]  # TODO replace it by the Form dataclass
Edge = tuple[Answer, int]  # Answer and number of time it has been selected
# TODO change the "Edge" name


@dataclass
class Question:  # TODO chek that 2 answer does not have the same text
    """Dataclass corresponding to one question stored in the database (a vertice/node in the database)"""

    question_id: str
    text: str
    answers: list[Answer]
    help_text: str
    type: str
    answers_choosen: AnswersList = field(default_factory=AnswersList)


@dataclass
class UserFeedback:
    """Dataclass correponding to all feedbacks of one user stored in the database"""

    user: Username
    feedbacks: list[Feedback]


@dataclass
class Form:
    """Dataclass corresponding to a Form completed by a user"""

    username: Username
    form_name: str
    question_list: list[Question]
    already_completed: bool
    modif_crypted: bool = False

    def __init__(self, already_completed: bool = False) -> None:
        self.question_list = []
        self.already_completed = already_completed

    def add_question(self, question: Question) -> None:
        if self.modif_crypted:  # We only take the proposition with modif_crytpted property set to false
            list_proposition = []
            for i in question.answers:
                if not i.modif_crypted:
                    list_proposition.append(i)
            question.answers = list_proposition
        self.question_list.append(question)

    def add_answers(self, answers: AnswersList, question_number: int) -> None:
        print(self.question_list)
        # /!\ hard code for modif_crypted here :
        if question_number < len(self.question_list):
            self.question_list = self.question_list[:question_number]
        print("ICIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
        print(self.question_list)
        self.question_list[-1].answers_choosen = answers
        if len(self.question_list) > 1 and self.question_list[1].answers_choosen[0].text == "Yes":
            self.modif_crypted = True

    def set_name(self, form_name: str) -> None:
        self.form_name = form_name

    def set_username(self, usename: Username) -> None:
        self.username = usename

    def calcul_best_ais(self, nb_ai: int, list_ai: list[str]) -> list[str]:
        raw_coef_ai = np.array([1.0] * len(list_ai))
        for question in self.question_list:
            for answer in question.answers_choosen:
                if answer.list_coef:
                    raw_coef_ai = np.multiply(raw_coef_ai, np.array(answer.list_coef))
        # we put all NaN value to -1
        coef_ai = [-1 if math.isnan(coef) else coef for coef in raw_coef_ai]
        list_bests_ais = []
        for index, ai_name in enumerate(list_ai):
            list_bests_ais.append((ai_name, coef_ai[index]))
        list_bests_ais.sort(key=lambda x: x[1], reverse=True)
        return []
        return [x[0] for x in list_bests_ais][:nb_ai]
