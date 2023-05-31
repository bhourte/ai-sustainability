"""File used to store all global variable list"""
NUMERATOR_METRICS = [
    "f1_score_handmade",
    "f1_score",
    "evaluation_accuracy",
    "r2_score",
    "score",
    "training_r2_score",
    "training_score",
    "accuracy_score",
    "true_negatives",
    "true_positives",
    "recall_score",
    "precision_score",
]  # Higher is beter
DENOMINATOR_METRICS = [
    "Duration",
    "false_negatives",
    "false_positives",
    "max_error",
    "mean_absolute_error",
    "mean_squared_error",
    "mean_absolute_percentage_error",
    "root_mean_squared_error",
    "training_mean_absolute_error",
    "training_mean_squared_error",
    "training_root_mean_squared_error",
    "log_loss",
]  # Lower is beter

METRIC_IMPLEMENTED = NUMERATOR_METRICS + DENOMINATOR_METRICS + ["precision_recall_auc", "roc_auc"]
