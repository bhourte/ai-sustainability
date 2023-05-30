"""File used for the business layer of the result displayer"""

from typing import Optional, Tuple

import numpy as np
from mlflow.entities.run import Run
from mlflow.store.entities import PagedList

from ai_validation.models import Model

POSITIVE_METRICS = [
    "f1_score_handmade",
    "f1_score",
    "evaluation_accuracy",
]
NEGATIVE_METRICS = [
    "Duration",
    "false_negatives",
    "false_positives",
    "max_error",
    "mean_absolute_error",
]


class Business:
    """Class used for all business task of the result displayer"""

    def __init__(self) -> None:
        pass

    def delete_accuracy(self, used_metric: list[str]) -> list[str]:
        """Method used to replace the Accuracy term by the good ones"""
        new_metrics: list[str] = []
        for i in used_metric:
            if i != "Accuracy":
                new_metrics.append(i)
        return new_metrics

    def get_ai_list(self, run_page: PagedList[Run]) -> Optional[list[Model]]:
        """
        Method used to create a list that link each ai with its normalized coeficient
        and its hyperparameters and its metrics
        """
        if not run_page:
            return None
        list_model: list[Model] = []
        for run in run_page:
            model_name = run.data.to_dictionary()["tags"]["mlflow.runName"]
            params = run.data.to_dictionary()["params"]
            metrics = run.data.to_dictionary()["metrics"]
            metrics["Duration"] = (
                run.info.end_time - run.info.start_time
            )  # TODO change Duration here, berk, depend of the computer speed
            list_model.append(Model(model_name, params, metrics))
        return list_model

    def set_and_normalize_one_metric(self, list_models: list[Model], used_metric: str) -> None:
        """Method used to set a normalized coeficient for one metric (used_metric)"""
        if used_metric in POSITIVE_METRICS:
            max_value = max(list(i.metrics[used_metric] for i in list_models))
            min_value = min(list(i.metrics[used_metric] for i in list_models))
            for model in list_models:
                model.normalized_metrics[used_metric] = (model.metrics[used_metric] - min_value) / (
                    max_value - min_value
                )
        elif used_metric in NEGATIVE_METRICS:
            max_value = max(list(1 / i.metrics[used_metric] for i in list_models))
            min_value = min(list(1 / i.metrics[used_metric] for i in list_models))
            for model in list_models:
                model.normalized_metrics[used_metric] = (1 / model.metrics[used_metric] - min_value) / (
                    max_value - min_value
                )
        elif used_metric == "Global score":
            list_coef = np.ones(len(list_models))
            for index, model in enumerate(list_models):
                for metric in POSITIVE_METRICS:
                    if metric in model.metrics.keys():
                        list_coef[index] = list_coef[index] * model.metrics[metric]
                for metric in NEGATIVE_METRICS:
                    if metric in model.metrics.keys():
                        list_coef[index] = list_coef[index] / model.metrics[metric]
            max_value = max(list(list_coef[i] for i in range(len(list_models))))
            min_value = min(list(list_coef[i] for i in range(len(list_models))))
            for index, model in enumerate(list_models):
                model.normalized_metrics[used_metric] = (list_coef[index] - min_value) / (max_value - min_value)
                print(model.normalized_metrics)
        else:
            raise NotImplementedError(f"Metric {used_metric} not implemented yet, choose an other one.")

    def set_normalized_metrics(self, list_model: list[Model], list_metrics: list[str]) -> None:
        """
        Method used to rank all AIs according to selected_metric
        Return : a list of Tuple(Model, float: normalized selected_metric)
        """
        for metric in list_metrics:
            self.set_and_normalize_one_metric(list_model, metric)
        self.set_and_normalize_one_metric(list_model, "Global score")

    def get_pareto_points(self, list_model: list[Model], metric1: str, metric2: str) -> list[Tuple[Model, bool]]:
        list_tuple = [(model, 0) for model in list_model]  # 0 = no yet tested, -1 = non-pareto, 1 = pareto
        list_tuple.sort(key=lambda x: x[0].normalized_metrics[metric1] + x[0].normalized_metrics[metric1], reverse=True)
        for i, (model_i, state) in enumerate(list_tuple):
            if state == 0:
                for j in range(i, len(list_tuple)):
                    if (
                        model_i.normalized_metrics[metric1] > list_tuple[j][0].normalized_metrics[metric1]
                        and model_i.normalized_metrics[metric2] > list_tuple[j][0].normalized_metrics[metric2]
                    ):
                        # j < i for the 2 metrics => j is not a pareto point
                        list_tuple[j] = (list_tuple[j][0], -1)
                    elif (
                        model_i.normalized_metrics[metric1] < list_tuple[j][0].normalized_metrics[metric1]
                        and model_i.normalized_metrics[metric2] < list_tuple[j][0].normalized_metrics[metric2]
                    ):
                        # We have find a biger one in the 2 metrics => i is not a pareto point
                        list_tuple[i] = (model_i, -1)
                        break
                    # if reach here, it's a pareto point => congrats!
                    list_tuple[i] = (model_i, 1)
        return [(i, j == 1) for i, j in list_tuple]
