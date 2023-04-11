from dataclasses import dataclass
from typing import NewType

Answer = NewType("Answer", list[str])
User = NewType("User", str)
Query = NewType("Query", str)
Feedback = NewType("Feedback", str)
AnswersList = NewType("AnswersList", list[Answer])


@dataclass
class Question:
    text: str
    answers: list[Answer]
    help_text: str
    type: str


@dataclass
class UserFeedback:
    user: User
    feedback: list[Feedback]


@dataclass
class SelectedEdge:
    edge: str
    text: str
    nb_selected: int
