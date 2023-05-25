"""File used to create an experiment with mlflow and give the needed metrics"""
from typing import Optional

import mlflow
from decouple import config
from mlflow.client import MlflowClient
from mlflow.exceptions import MlflowException


class MlFlow:
    """Class used to create experiment in mlflow after a form is completed"""

    def __init__(self) -> None:
        pass

    def create_experiment(self, name: str, description: str) -> Optional[str]:
        """create an mlflow experiment and return the used metrics"""
        mlflow.set_tracking_uri(config("URI"))
        try:
            experiment_id = mlflow.set_experiment(name).experiment_id
            with mlflow.start_run() as run:
                mlflow.set_experiment_tag("mlflow.note.content", description)
            mlflow.delete_run(run.info.run_id)
            return experiment_id
        except MlflowException:
            return None

    def change_experiment_name(self, old_name: str, new_name: str) -> Optional[str]:
        """Change the name of an existing mlflow experiment"""
        try:
            client = MlflowClient(config("URI"))
            experiment_id = client.get_experiment_by_name(old_name).experiment_id
            client.rename_experiment(str(experiment_id), new_name)
            return experiment_id
        except MlflowException:
            return None
