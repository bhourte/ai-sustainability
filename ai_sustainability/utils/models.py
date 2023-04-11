"""
File with all dataclass and Type we use in the form application
"""

from dataclasses import dataclass
from typing import NewType

# TODO : distinguish between answer given by an user an list of answers of a question
QuestionAnswer = NewType("QuestionAnswer", list[str])  # List of answers possible for a question
UserAnswer = NewType("UserAnswer", list[str])  # List of answers selected by the user in QuestionAnswer propositions
User = NewType("User", str)
Query = NewType("Query", str)
Feedback = NewType("Feedback", str)
AnswersList = NewType("AnswersList", list[UserAnswer])


@dataclass
class Question:
    """Dataclass corresponding to one question stored in the database"""

    question_id: str
    text: str
    answers: list[QuestionAnswer]
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
