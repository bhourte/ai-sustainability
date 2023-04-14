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

from dataclasses import dataclass, field
from typing import NewType

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


AnswersList = list[Answer]  # List of answers selected by the user in QuestionAnswer propositions
FormAnswers = list[AnswersList]


@dataclass
class Question:  # TOTO chek that 2 answer does not have the same text
    """Dataclass corresponding to one question stored in the database (a vertice/node in the database)"""

    question_id: str
    text: str
    answers: list[Answer]
    help_text: str
    type: str


@dataclass
class UserFeedback:
    """Dataclass correponding to all feedbacks of one user stored in the database"""

    user: Username
    feedbacks: list[Feedback]


@dataclass
class Edge:
    """Dataclass corresponding to an edges and the number of time it has been selected"""  # TODO faire une bonne description (ou changer le nom)

    # TODO changer ca en un tuple (Answer, nb_times_selected)
    answer_id: str
    text: str
    nb_selected: int

    @property
    def question_in_id(self) -> str:
        return self.answer_id.split("-")[0]

    @property
    def question_out_id(self) -> str:
        return self.answer_id.split("-")[1]

    def __repr__(self) -> str:
        return f"Q {self.question_in_id} to Q {self.question_out_id}"
