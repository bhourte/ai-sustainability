"""File for all Dataclass, NewType and Alias"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Experiment:
    """Dataclass correponding an mlflow experiment"""

    experiment_id: str
    experiment_name: str
    experiment_user: Optional[str]


@dataclass
class Model:
    """Dataclass corresponding to a model, with all parameters and metrics"""

    model_name: str
    parameters: dict
    metrics: dict
    normalized_metrics: dict = field(default_factory=dict)

    def set_duration(self, duration: float) -> None:
        self.metrics["Duration"] = duration

    def get_param_explainer(self) -> str:
        """Method used to get a string explaining all params of a single run"""
        return "There are all used hyperparameters for this AI :  \n" + "  \n".join(
            [f"{i} : {self.parameters[i]}" for i in self.parameters]
        )

    def get_metrics_expaliner(
        self, metric_used: list[str], get_all_metrics: bool = False, normalized: bool = False
    ) -> str:
        """Method used to get a string explaining all metrics and their value of a single run"""
        list_metrics: list[str] = ["There are all used metrics for this AI :"]
        if not normalized:
            for i in self.metrics:
                if i in metric_used or get_all_metrics:
                    list_metrics.append(f"{i} : {self.metrics[i]}")
        else:
            for i in self.normalized_metrics:
                if i in metric_used or get_all_metrics:
                    list_metrics.append(f"{i} : {self.normalized_metrics[i]}")
        return "  \n".join(list_metrics)
