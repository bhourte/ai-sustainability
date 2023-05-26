"""File used for all application layer of the result part of the application"""


from typing import Optional, Tuple

from ai_validation.business import Business
from ai_validation.db_access import DbAccess
from ai_validation.mlflow_access import MlflowConnector
from ai_validation.models import Experiment


class Application:
    """Application layer"""

    def __init__(self) -> None:
        self.database = DbAccess()
        self.mlflow_connector = MlflowConnector()
        self.business = Business()

    def get_all_user(self) -> list[str]:
        return self.database.get_all_users()

    def get_form_id(self, experiment_id: str) -> str:
        return self.database.get_form_id(experiment_id)

    def get_metrics(self, form_id: str, replace_accuracy: bool = True) -> list[str]:
        # Use replace_accuracy if an "Accuracy" metric is log in the mlflow experience
        raw_metrics = self.database.get_all_metrics(form_id)
        return self.business.replace_accuracy(raw_metrics) if replace_accuracy else raw_metrics

    def get_experiment_from_user(self, selected_user: Optional[str]) -> Optional[list[Experiment]]:
        id_list = self.database.get_experiment_id(selected_user)
        return self.mlflow_connector.get_experiment(selected_user, id_list)

    def get_ai_from_experiment(
        self, selected_experiment_id: str, used_metric: list[str]
    ) -> Optional[list[Tuple[str, float, str, str]]]:
        """
        Function used to get all ai raked and there hyper parameters
        Return : list[(ai_name:str, coef:float, param_expaliner:str, metrics_explainer:str)]
        """
        selected_experiment_name = self.mlflow_connector.get_experiment_name(selected_experiment_id)
        selected_experiment = selected_experiment_name.split("-")
        if len(selected_experiment) <= 2:
            return None
        run_page = self.mlflow_connector.get_run_page(selected_experiment_id)
        return self.business.rank_ais(run_page, used_metric)
