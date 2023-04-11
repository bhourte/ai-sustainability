from dataclasses import dataclass
from typing import NewType

Answer = NewType("Answer", str)


@dataclass
class Question:
    question_text: str
    answers: list[Answer]
    help_text: str
    question_label: str
