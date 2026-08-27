import os

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import train_test_split

from src.ml.recovery_model import (
    RecoveryProbabilityModel
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "data"

CUSTOMERS_FILE = os.path.join(
    DATA_DIR,
    "customers.csv"
)

TRANSACTIONS_FILE = os.path.join(
    DATA_DIR,
    "transactions.csv"
)

PAYMENT_ATTEMPTS_FILE = os.path.join(
    DATA_DIR,
    "payment_attempts.csv"
)

RECOVERY_OUTCOMES_FILE = os.path.join(
    DATA_DIR,
    "recovery_outcomes.csv"
)

MODEL_DIR = "models"

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "recovery_probability_model.joblib"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading datasets...")

customers_df = pd.read_csv(
    CUSTOMERS_FILE
)

transactions_df = pd.read_csv(
    TRANSACTIONS_FILE
)

payment_attempts_df = pd.read_csv(
    PAYMENT_ATTEMPTS_FILE
)

recovery_outcomes_df = pd.read_csv(
    RECOVERY_OUTCOMES_FILE
)


# ============================================================
# PREPARE CUSTOMER FEATURES
# ============================================================

customer_features = customers_df[
    [
        "customer_id",
        "customer_tenure_days",
        "historical_success_rate",
        "avg_transaction_amount",
    ]
].copy()


# ============================================================
# PREPARE ATTEMPT FEATURES
# ============================================================

attempt_features = (
    payment_attempts_df
    .groupby(
        "transaction_id",
        as_index=False
    )[
        "attempt_number"
    ]
    .max()
)


# ============================================================
# PREPARE TRANSACTION FEATURES
# ============================================================

transaction_features = transactions_df[
    [
        "transaction_id",
        "customer_id",
        "amount",
        "payment_method",
        "bank",
        "transaction_time",
        "failure_reason",
        "checkout_completed",
        "subscription_flag",
        "status",
    ]
].copy()


transaction_features[
    "transaction_time"
] = pd.to_datetime(
    transaction_features[
        "transaction_time"
    ]
)


transaction_features[
    "transaction_hour"
] = (
    transaction_features[
        "transaction_time"
    ].dt.hour
)


# ============================================================
# PREPARE TARGET
# ============================================================

target_df = recovery_outcomes_df[
    [
        "transaction_id",
        "recovered",
    ]
].copy()


target_df[
    "recovered"
] = (
    target_df[
        "recovered"
    ]
    .astype(bool)
    .astype(int)
)


# ============================================================
# MERGE DATASETS
# ============================================================

dataset = (
    transaction_features

    .merge(
        customer_features,
        on="customer_id",
        how="inner"
    )

    .merge(
        attempt_features,
        on="transaction_id",
        how="inner"
    )

    .merge(
        target_df,
        on="transaction_id",
        how="inner"
    )
)


# ============================================================
# KEEP FAILED TRANSACTIONS ONLY
# ============================================================

dataset = dataset[
    dataset[
        "status"
    ] == "failed"
].copy()


print(
    f"\nTraining records: "
    f"{len(dataset):,}"
)


# ============================================================
# VERIFY TARGET
# ============================================================

print(
    "\nRecovery outcome distribution:"
)

print(
    dataset[
        "recovered"
    ].value_counts()
)


# ============================================================
# DEFINE FEATURES
# ============================================================

feature_columns = [

    "amount",

    "attempt_number",

    "historical_success_rate",

    "customer_tenure_days",

    "avg_transaction_amount",

    "transaction_hour",

    "payment_method",

    "bank",

    "failure_reason",

    "checkout_completed",

    "subscription_flag",
]


X = dataset[
    feature_columns
].copy()


y = dataset[
    "recovered"
].copy()


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = (
    train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42,

        stratify=y,
    )
)


print(
    f"\nTraining set: "
    f"{len(X_train):,}"
)

print(
    f"Test set: "
    f"{len(X_test):,}"
)


# ============================================================
# TRAIN MODEL
# ============================================================

print(
    "\nTraining Recovery Probability Model..."
)

model = RecoveryProbabilityModel()

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTIONS
# ============================================================

y_probability = (
    model.predict_probability(
        X_test
    )
)

y_prediction = (
    model.predict(
        X_test
    )
)


# ============================================================
# CLASSIFICATION METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_prediction
)

precision = precision_score(
    y_test,
    y_prediction,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_prediction,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_prediction,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

brier = brier_score_loss(
    y_test,
    y_probability
)


# ============================================================
# PRINT METRICS
# ============================================================

print(
    "\n=========================================="
)

print(
    "Recovery Probability Model Evaluation"
)

print(
    "=========================================="
)

print(
    f"\nAccuracy:  {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall:    {recall:.4f}"
)

print(
    f"F1 Score:  {f1:.4f}"
)

print(
    f"ROC-AUC:   {roc_auc:.4f}"
)

print(
    f"Brier:     {brier:.4f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print(
    "\nClassification report:"
)

print(
    classification_report(
        y_test,
        y_prediction,
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print(
    "Confusion matrix:"
)

print(
    confusion_matrix(
        y_test,
        y_prediction
    )
)


# ============================================================
# PROBABILITY SUMMARY
# ============================================================

print(
    "\nPredicted probability summary:"
)

probability_series = pd.Series(
    y_probability
)

print(
    probability_series.describe()
)


# ============================================================
# SAVE MODEL
# ============================================================

model.save(
    MODEL_FILE
)


print(
    f"\nModel saved to:"
    f"\n{MODEL_FILE}"
)


# ============================================================
# SAVE TEST PREDICTIONS
# ============================================================

test_results = X_test.copy()

test_results[
    "actual_recovered"
] = y_test.values

test_results[
    "predicted_recovered"
] = y_prediction

test_results[
    "recovery_probability"
] = y_probability


test_output_file = os.path.join(
    DATA_DIR,
    "recovery_model_test_results.csv"
)


test_results.to_csv(
    test_output_file,
    index=False
)


print(
    f"\nTest predictions saved to:"
    f"\n{test_output_file}"
)


print(
    "\n=========================================="
)

print(
    "Model training completed."
)

print(
    "==========================================\n"
)