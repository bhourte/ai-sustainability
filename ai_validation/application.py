"""File used for all application layer of the result part of the application"""


from typing import Optional, Tuple

from ai_sustainability.package_business.models import Username
from ai_validation.business import Business
from ai_validation.db_access import DbAccess
from ai_validation.mlflow_access import MlflowConnector


class Application:
    """Application layer"""

    def __init__(self) -> None:
        self.database = DbAccess()
        self.mlflow_connector = MlflowConnector()
        self.business = Business()

    def get_all_user(self) -> list[Username]:
        return self.database.get_all_users()

    def get_experiment_from_user(
        self, selected_user: Username, all_user: bool = False
    ) -> Optional[Tuple[list[str], list[str]]]:
        return self.mlflow_connector.get_experiment(selected_user, all_user)

    def get_ai_from_experiment(self, selected_experiment_id: str) -> Optional[Tuple[list, list]]:
        """
        Function used to get all ai raked and there hyper parameters
        Return : list[(ai_name:str, coef:float, param:str)]
        """
        selected_experiment_name = self.mlflow_connector.get_experiment_name(selected_experiment_id)
        run_page = self.mlflow_connector.get_one_run(selected_experiment_id)
        selected_experiment = selected_experiment_name.split("-")
        if len(selected_experiment) <= 2:
            return None
        used_metric = self.database.get_all_metrics(Username(selected_experiment[-2]), selected_experiment[-1])
        return self.business.rank_ais(run_page, used_metric)
