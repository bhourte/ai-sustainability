"""File used to create an experiment with mlflow and give the needed metrics"""
from typing import Optional

import mlflow
from mlflow.exceptions import MlflowException


def create_experiment(uri: str, name: str) -> Optional[str]:
    """create an mlflow experiment and return the used metrics"""
    mlflow.set_tracking_uri(uri)
    try:
        return mlflow.set_experiment(name).experiment_id
    except MlflowException:
        return None
