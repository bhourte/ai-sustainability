"""
File with all dataclass and Type we use in the form application

New models :
  NewType :
    - User
    - Query
    - Feedback
    - UserAnswers
    - AnswersStats
  Dataclass :
    - Answer
    - Question
    - UserFeedback
    - Form
"""

import math
from dataclasses import dataclass, field
from typing import NewType, Optional, Tuple

import numpy as np

from ai_sustainability.utils import get_n_best

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
    metric: Optional[str] = None
    list_coef: list[float] = field(default_factory=list)

    @property
    def _question_in_id(self) -> str:
        return self.answer_id.split("-")[0]

    @property
    def _question_out_id(self) -> str:
        return self.answer_id.split("-")[1]

    def __repr__(self) -> str:
        return f"Q{self._question_in_id} to Q{self._question_out_id}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Answer):
            if self.answer_id == other.answer_id or self.text == other.text:
                return True
        return False

    @classmethod
    def create_end_answer(cls) -> "Answer":
        return Answer(answer_id="end", text="end", help_text="", modif_crypted=False, metric=None, list_coef=[])


AnswersList = list[Answer]  # List of answers selected by the user in QuestionAnswer propositions
AnswersStats = tuple[Answer, int]  # Answer and number of time it has been selected


@dataclass
class Question:
    """Dataclass corresponding to one question stored in the database (a vertice/node in the database)"""

    question_id: str
    text: str
    type: str
    _possible_answers: list[Answer] = field(default_factory=AnswersList)
    choosen_answers: AnswersList = field(default_factory=AnswersList)

    @property
    def help_text(self) -> str:
        return self._help_text + "  \n".join(
            f"{answer_i.text} : {answer_i.help_text}" for answer_i in self.possible_answers
        )

    @help_text.setter
    def help_text(self, value: str) -> None:
        self._help_text = value

    @property
    def possible_answers(self) -> list[Answer]:
        return self._possible_answers

    @possible_answers.setter
    def possible_answers(self, answers_list: list[Answer]) -> None:
        """Check that 2 Answer does not have the same text and set self.answers"""
        for i, answer_i in enumerate(answers_list):
            for j in range(i + 1, len(answers_list)):
                if answer_i == answers_list[j]:
                    raise ValueError("A Question can not have 2 Answer with the same text")
        self._possible_answers = answers_list

    def maj_answers_crypted(self) -> None:
        """Only keep answers with modif_crypted == false"""
        new_answers_list: list[Answer] = []
        for answer in self.possible_answers:
            if not answer.modif_crypted:
                new_answers_list.append(answer)
        self.possible_answers = new_answers_list


@dataclass
class UserFeedback:
    """Dataclass correponding to all feedbacks of one user stored in the database"""

    user: Username
    feedbacks: list[Feedback]


@dataclass
class Form:
    """Dataclass corresponding to a Form completed by a user"""

    username: Optional[Username] = None
    question_list: list[Question] = field(default_factory=list)
    form_name: str = ""
    already_completed: bool = False
    experiment_id: Optional[str] = None

    @property
    def last_question(self) -> Question:
        return self.question_list[-1]

    @property
    def modif_crypted(self) -> bool:
        if not self.question_list or len(self.question_list) < 2:
            return False
        return self.question_list[1].choosen_answers[0].text == "Yes"

    def add_question(self, question: Question) -> None:
        if self.modif_crypted:  # We only take the proposition with modif_crytpted property set to false
            question.maj_answers_crypted()
        self.question_list.append(question)

    def add_answers(self, answers: AnswersList, question_number: int) -> None:
        if self.already_completed:
            if not self.check_changes(answers, question_number):
                return
        is_not_last_question = question_number < len(self.question_list)
        if not self.already_completed and is_not_last_question:
            self.question_list = self.question_list[:question_number]
        self.last_question.choosen_answers = answers

    def check_changes(self, answers: AnswersList, question_number: int) -> bool:
        question = self.question_list[question_number - 1]
        if len(answers) != len(question.choosen_answers):
            self.already_completed = False
            return True
        for index, answer in enumerate(answers):
            if answer.text != question.choosen_answers[index].text:
                self.already_completed = False
                return True
        return False

    def calcul_best_ais(self, nb_ai: int, list_ai: list[str]) -> list[Tuple[str, float]]:
        raw_coef_ai = np.array([1.0] * len(list_ai))
        for question in self.question_list:
            for answer in question.choosen_answers:
                if answer.list_coef:
                    raw_coef_ai = np.multiply(raw_coef_ai, np.array(answer.list_coef))
        # we put all NaN value to -1
        coef_ai = [-1 if math.isnan(coef) else coef for coef in raw_coef_ai]
        list_bests_ais = []
        for index, ai_name in enumerate(list_ai):
            list_bests_ais.append((ai_name, coef_ai[index]))
        return get_n_best(nb_ai, list_bests_ais)
