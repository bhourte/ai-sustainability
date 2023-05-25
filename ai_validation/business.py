"""File used for the business layer of the result displayer"""

from typing import Optional, Tuple

import numpy as np
from mlflow.entities.run import Run
from mlflow.store.entities import PagedList


class Business:
    """Class used for all business task of the result displayer"""

    def __init__(self) -> None:
        pass

    def replace_accuracy(self, used_metric: list[str]) -> list[str]:
        """Method used to replace the Accuracy term by the good ones"""
        new_metrics: list[str] = []
        for i in used_metric:
            if i == "Accuracy":
                for j in used_metric:
                    if j in [
                        "f1_score_handmade",
                        "f1_score",
                        "evaluation_accuracy",
                        "max_error",
                        "mean_absolute_error",
                    ]:
                        new_metrics.append(j)
            else:
                new_metrics.append(i)
        return new_metrics

    def get_param(self, run: Run) -> str:
        """Method used to get a string explaining all params of a single run"""
        dico = run.data.to_dictionary()["params"]
        return "There are all used hyperparameters for this AI :" + "  \n".join([f"{i} : {dico[i]}" for i in dico])

    def get_metrics(self, run: Run, metric_used: list[str]) -> str:
        """Method used to get a string explaining all metrics and their value of a single run"""
        dico = run.data.to_dictionary()["metrics"]
        list_metrics: list[str] = ["There are all used metrics for this AI :"]
        for i in dico:
            if i in metric_used:
                list_metrics.append(f"{i} : {dico[i]}")
        if "Duration" in metric_used:
            list_metrics.append(f"Duration : {run.info.end_time - run.info.start_time} ms")
        return "  \n".join(list_metrics)

    def create_coef_matrix(
        self, run_page: PagedList[Run], used_metric: list[str]
    ) -> Tuple[np.ndarray, list[str], list[str], list[str]]:
        """
        Method used to create a matrix with all the normalized coeficient for all runs and all metrics (but not only)
        return : [
            - matrix of coef
            - list of coresponding AIs
            - list of string explaining hyperparameters choosen
            - list of string explaining metrics obtained
        ]
        """
        list_ai: list[str] = []
        list_params: list[str] = []
        list_metrics: list[str] = []
        list_coef = np.zeros((len(used_metric), len(run_page)))

        for i, run_i in enumerate(run_page):
            run_data = run_i.data.to_dictionary()
            for j, metric_j in enumerate(used_metric):
                if metric_j not in run_data["metrics"]:
                    if metric_j == "Duration":
                        list_coef[j][i] = run_i.info.end_time - run_i.info.start_time
                    else:
                        raise RuntimeError("Error, needed metrics not log in the mlflow run")
                else:
                    list_coef[j][i] = run_data["metrics"][metric_j]

            list_ai.append(run_i.info.run_name)
            list_params.append(self.get_param(run_i))
            list_metrics.append(self.get_metrics((run_i), used_metric))
        return list_coef, list_ai, list_params, list_metrics

    def create_ai_list_with_coef(
        self,
        list_coef: np.ndarray,
        list_ai: list[str],
        used_metric: list[str],
        list_params: list[str],
        list_metrics: list[str],
    ) -> list[Tuple[str, float, str, str]]:
        """
        Method used to create a list that link each ai with its normalized coeficient
        and its hyperparameters and its metrics
        """
        for i, elmt_i in enumerate(list_coef):
            # 2 way to normalize coeficients (if higher is beter or worse)
            if used_metric[i] in [
                "f1_score_handmade",
                "f1_score",
                "evaluation_accuracy",
            ]:
                list_coef[i] = elmt_i / max(elmt_i)
            elif used_metric[i] in [
                "Duration",
                "false_negatives",
                "false_positives",
                "max_error",
                "mean_absolute_error",
            ]:
                list_coef[i] = min(elmt_i) / elmt_i
            else:
                raise NotImplementedError("A not implemented metric has been stored in the database answer, how ???")
        list_coef = list_coef.T
        return [(ai_i, np.prod(list_coef[i]), list_params[i], list_metrics[i]) for i, ai_i in enumerate(list_ai)]

    def rank_ais(self, run_page: PagedList[Run], used_metric: list[str]) -> Optional[Tuple[list, list]]:
        """
        Method used to rank all ais an return them in an ordered list of tuple
        and return also the list of used metrics
        """
        if not run_page:
            return None

        used_metric = self.replace_accuracy(used_metric)
        print(used_metric)
        list_coef, list_ai, list_params, list_metrics = self.create_coef_matrix(run_page, used_metric)

        list_ranking = self.create_ai_list_with_coef(list_coef, list_ai, used_metric, list_params, list_metrics)

        list_ranking.sort(key=lambda x: x[1], reverse=True)
        return list_ranking, used_metric
