"""File for all Dataclass, NewType and Alias"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Experiment:
    """Dataclass correponding an mlflow experiment"""

    experiment_id: str
    experiment_name: str
    experiment_user: Optional[str]
