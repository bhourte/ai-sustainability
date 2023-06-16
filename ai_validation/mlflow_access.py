"""File used to connect to an mlflow to retreive all information about test run"""

from typing import Optional

from decouple import config
from mlflow.entities.run import Run
from mlflow.exceptions import MlflowException
from mlflow.store.entities import PagedList
from mlflow.tracking import MlflowClient

from ai_validation.global_variables import METRIC_IMPLEMENTED
from ai_validation.models import Experiment, Model


class MlflowConnector:
    """Class used to connect to an mlflow server"""

    def __init__(self) -> None:
        self.client = MlflowClient(tracking_uri=config("URI"))

    def get_experiment(self, selected_user: Optional[str], id_list: list[str]) -> Optional[list[Experiment]]:
        """Method used to get all experiment name and id from a username"""
        try:
            experiments = self.client.search_experiments()
        except MlflowException:
            return None
        list_experiment: list[Experiment] = []
        for i in experiments:
            if i.experiment_id in id_list or selected_user is None:
                list_experiment.append(Experiment(i.experiment_id, i.name, selected_user))
        return list_experiment

    def get_experiment_name(self, experiment_id: str) -> str:
        return self.client.get_experiment(experiment_id).name

    def get_run_page(self, selected_experiment_id: str) -> PagedList[Run]:
        return self.client.search_runs([selected_experiment_id])

    def get_all_metrics(self, experiment_id: str) -> Optional[list[str]]:
        run_page = self.get_run_page(experiment_id)
        if not run_page:
            return None
        list_metrics: list[str] = []
        for metric in list(run_page[0].data.to_dictionary()["metrics"].keys()):
            if metric in METRIC_IMPLEMENTED:
                list_metrics.append(metric)

        return ["Duration"] + list_metrics

    def get_artifact_uri(self, selected_experiment: Experiment, selected_models: Model) -> Optional[str]:
        run_page = self.get_run_page(selected_experiment.experiment_id)
        for run in run_page:
            if run.data.to_dictionary()["params"]["model_name"] == selected_models.model_name:
                return run.info.artifact_uri
        return None
