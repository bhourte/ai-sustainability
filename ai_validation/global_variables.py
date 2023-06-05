"""File used to store all global variable list"""
NUMERATOR_METRICS = [  # Higher is beter
    "accuracy",
    "accuracy_score",
    "evaluation_accuracy",
    "f1_score_handmade",
    "f1_score",
    "precision_score",
    "r2_score",
    "recall_score",
    "score",
    "training_f1_score",
    "training_precision_score",
    "training_r2_score",
    "training_score",
    "true_negatives",
    "true_positives",
    "val_accuracy",
]
DENOMINATOR_METRICS = [  # Lower is beter
    "Duration",
    "evaluation_loss",
    "false_negatives",
    "false_positives",
    "log_loss",
    "loss",
    "max_error",
    "mean_absolute_error",
    "mean_absolute_percentage_error",
    "mean_squared_error",
    "root_mean_squared_error",
    "training_log_loss",
    "training_mean_absolute_error",
    "training_mean_squared_error",
    "training_root_mean_squared_error",
    "val_loss",
]

METRIC_IMPLEMENTED = NUMERATOR_METRICS + DENOMINATOR_METRICS + ["precision_recall_auc", "roc_auc", "stopped_epoch"]
