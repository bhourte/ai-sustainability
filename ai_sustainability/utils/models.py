"""
File with all dataclass and Type we use in the form application
"""

from dataclasses import dataclass
from typing import NewType

UserAnswers = list[str]  # List of answers selected by the user in QuestionAnswer propositions for one question
User = NewType("User", str)
Query = NewType("Query", str)
Feedback = NewType("Feedback", str)
AnswersList = list[UserAnswers]  # List of answers selected by the user for all questions


@dataclass
class Proposition:
    """Dataclass corresponding to one proposition for a question"""

    proposition_id: str
    text: str
    help_text: str
    modif_crypted: bool


@dataclass
class Question:
    """Dataclass corresponding to one question stored in the database"""

    question_id: str
    text: str
    answers: list[Proposition]
    help_text: str
    type: str


@dataclass
class UserFeedback:
    """Dataclass correponding to all feedbacks of one user stored in the database"""

    user: User
    feedback: list[Feedback]


@dataclass
class SelectedEdge:
    """Dataclass corresponding to an edges and the number of time it has been selected"""

    edge: str
    text: str
    nb_selected: int
