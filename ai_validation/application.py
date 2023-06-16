"""File used for all application layer of the result part of the application"""


from typing import Optional, Tuple

from ai_validation.business import Business
from ai_validation.db_access import DbAccess
from ai_validation.mlflow_access import MlflowConnector
from ai_validation.models import Experiment, Model


class Application:
    """Application layer"""

    def __init__(self) -> None:
        self.database = DbAccess()
        self.mlflow_connector = MlflowConnector()
        self.business = Business()

    def get_all_user(self) -> list[str]:
        return self.database.get_all_users()

    def get_form_id(self, experiment_id: str) -> Optional[str]:
        return self.database.get_form_id(experiment_id)

    def get_metrics(self, form_id: str, delete_accuracy: bool = True) -> list[str]:
        # Use delete_accuracy if an "Accuracy" metric is log in the mlflow experience
        # a score parameters it's alway log before but with an other name (max_error, f1_score, etc.)
        raw_metrics = self.database.get_metrics_from_form(form_id)
        return self.business.delete_accuracy(raw_metrics) if delete_accuracy else raw_metrics

    def get_experiment_from_user(self, selected_user: Optional[str]) -> Optional[list[Experiment]]:
        id_list = self.database.get_experiment_id(selected_user)
        return self.mlflow_connector.get_experiment(selected_user, id_list)

    def get_model_from_experiment(self, selected_experiment_id: str) -> Optional[list[Model]]:
        run_page = self.mlflow_connector.get_run_page(selected_experiment_id)
        return self.business.get_ai_list(run_page)

    def set_normalized_metrics(
        self, model_list: list[Model], list_metrics: list[str], form_list_metrics: Optional[list[str]] = None
    ) -> None:
        self.business.set_normalized_metrics(model_list, list_metrics, form_list_metrics)

    def get_pareto_points(self, list_model: list[Model], metric1: str, metric2: str) -> list[Tuple[Model, bool]]:
        return self.business.get_pareto_points(list_model, metric1, metric2)

    def get_all_metrics(self, experiment_id: str) -> Optional[list[str]]:
        return self.mlflow_connector.get_all_metrics(experiment_id)

    def get_artifact_path(self, selected_experiment: Experiment, selected_models: Optional[Model]) -> Optional[str]:
        if selected_models is None:
            return None
        artifact_uri = self.mlflow_connector.get_artifact_uri(selected_experiment, selected_models)
        return None if artifact_uri is None else "mlartifacts" + artifact_uri.rsplit(":", maxsplit=1)[-1]
