"""File with all mlflow log function to log all metrics and parameters"""
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, f1_score


def log_confusion_matrix(y_true, y_pred) -> None:
    """Function used to log the confusion matrix figure"""
    matrix = confusion_matrix(y_true, y_pred)
    mlflow.log_figure(ConfusionMatrixDisplay(matrix).plot().figure_, "confusion_matrix_handmade.png")


def log_fn_and_fp(y_true, y_pred) -> None:
    """Function used to log the FN and FP metrics"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    mlflow.log_metric("false_negatives", fn)
    mlflow.log_metric("false_positives", fp)
    mlflow.log_metric("true_negatives", tn)
    mlflow.log_metric("true_positives", tp)


def log_f1_score(y_true, y_pred) -> None:
    """Function used to log the F1 score metric"""
    f1 = f1_score(y_true, y_pred, average="micro")
    mlflow.log_metric("f1_score_handmade", f1)


def log_parameters(data_train, data_test, model_name) -> None:
    """Function used to log the used parameters"""
    mlflow.log_param("nb_samples_train", len(data_train))
    mlflow.log_param("nb_samples_test", len(data_test))
    mlflow.log_param("model_name", model_name)
