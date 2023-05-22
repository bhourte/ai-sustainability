"""File used to create an experiment with mlflow and give the needed metrics"""
from typing import Optional

import mlflow


def create_experiment(uri: str, name: str) -> Optional[str]:
    """create an mlflow experiment and return the used metrics"""
    mlflow.set_tracking_uri(uri)
    try:
        experiment_id = mlflow.set_experiment(name).experiment_id
    except:
        experiment_id = None
    return experiment_id
