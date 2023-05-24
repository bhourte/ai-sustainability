"""File used to connect to an mlflow to retreive all information about test run"""

from typing import Optional, Tuple

from decouple import config
from mlflow.entities.run import Run
from mlflow.exceptions import MlflowException
from mlflow.store.entities import PagedList
from mlflow.tracking import MlflowClient


class MlflowConnector:
    """Class used to connect to an mlflow server"""

    def __init__(self) -> None:
        self.client = MlflowClient(tracking_uri=config("URI"))

    def get_experiment(self, selected_user: str, all_user: bool = False) -> Optional[Tuple[list[str], list[str]]]:
        """Method used to get all experiment name from a username"""
        try:
            experiments = self.client.search_experiments()
        except MlflowException:
            return None
        if not all_user:  # If we need to only keep experiment of a specific user
            new_list = []
            for i in experiments:
                if len(i.name.split("-")) > 1 and i.name.split("-")[1] == selected_user:
                    new_list.append(i)
            experiments = new_list
        return ([i.name for i in experiments], [i.experiment_id for i in experiments])

    def get_experiment_name(self, experiment_id: str) -> str:
        return self.client.get_experiment(experiment_id).name

    def get_one_run(self, selected_experiment_id: str) -> PagedList[Run]:
        return self.client.search_runs([selected_experiment_id])
