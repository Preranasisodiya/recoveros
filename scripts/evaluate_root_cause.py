import os

import pandas as pd

from src.root_cause.root_cause_engine import (
    RootCauseEngine
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


# ============================================================
# LOAD DATA
# ============================================================

customers_df = pd.read_csv(
    CUSTOMERS_FILE
)

transactions_df = pd.read_csv(
    TRANSACTIONS_FILE
)

payment_attempts_df = pd.read_csv(
    PAYMENT_ATTEMPTS_FILE
)


# ============================================================
# PREPARE CUSTOMER FEATURES
# ============================================================

customer_features = customers_df[
    [
        "customer_id",
        "historical_success_rate",
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
# MERGE DATA
# ============================================================

evaluation_df = (
    transactions_df
    .merge(
        customer_features,
        on="customer_id",
        how="left"
    )
    .merge(
        attempt_features,
        on="transaction_id",
        how="left"
    )
)


# ============================================================
# SELECT FAILED TRANSACTIONS
# ============================================================

failed_df = evaluation_df[
    evaluation_df[
        "status"
    ] == "failed"
].copy()


failed_df[
    "attempt_number"
] = (
    failed_df[
        "attempt_number"
    ]
    .fillna(1)
    .astype(int)
)


# ============================================================
# CREATE ROOT CAUSE ENGINE
# ============================================================

engine = RootCauseEngine()


# ============================================================
# RUN ROOT CAUSE ANALYSIS
# ============================================================

results = []


for _, row in failed_df.iterrows():

    transaction = {

        "transaction_id":
            row["transaction_id"],

        "amount":
            row["amount"],

        "failure_reason":
            row["failure_reason"],

        "attempt_number":
            row["attempt_number"],
    }

    result = engine.analyze(
        transaction
    )

    results.append({

        "transaction_id":
            result["transaction_id"],

        "amount":
            row["amount"],

        "failure_reason":
            row["failure_reason"],

        "attempt_number":
            row["attempt_number"],

        "root_cause":
            result["root_cause"],

        "cause_category":
            result["cause_category"],

        "nature":
            result["nature"],

        "confidence":
            result["confidence"],

        "recommended_direction":
            result[
                "recommended_direction"
            ],
    })


results_df = pd.DataFrame(
    results
)


# ============================================================
# HEADER
# ============================================================

print("\n==========================================")
print("RecoverOS Root Cause Engine Evaluation")
print("==========================================")


print(
    f"\nTotal transactions: "
    f"{len(transactions_df):,}"
)

print(
    f"Failed transactions evaluated: "
    f"{len(results_df):,}"
)


# ============================================================
# CAUSE CATEGORY DISTRIBUTION
# ============================================================

print(
    "\nRoot cause category distribution:"
)

category_distribution = (
    results_df[
        "cause_category"
    ]
    .value_counts()
)

print(
    category_distribution
)


# ============================================================
# CAUSE CATEGORY PERCENTAGES
# ============================================================

print(
    "\nRoot cause category percentages:"
)

category_percentages = (
    results_df[
        "cause_category"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)

for category, percentage in (
    category_percentages.items()
):

    print(
        f"{category}: "
        f"{percentage:.2f}%"
    )


# ============================================================
# TEMPORARY VS PERSISTENT
# ============================================================

print(
    "\nFailure nature distribution:"
)

nature_distribution = (
    results_df[
        "nature"
    ]
    .value_counts()
)

print(
    nature_distribution
)


# ============================================================
# RECOVERY DIRECTION
# ============================================================

print(
    "\nRecommended recovery direction:"
)

direction_distribution = (
    results_df[
        "recommended_direction"
    ]
    .value_counts()
)

print(
    direction_distribution
)


# ============================================================
# CONFIDENCE
# ============================================================

average_confidence = (
    results_df[
        "confidence"
    ].mean()
)

minimum_confidence = (
    results_df[
        "confidence"
    ].min()
)

maximum_confidence = (
    results_df[
        "confidence"
    ].max()
)


print(
    "\nRoot cause confidence:"
)

print(
    f"Average: "
    f"{average_confidence:.4f}"
)

print(
    f"Minimum: "
    f"{minimum_confidence:.4f}"
)

print(
    f"Maximum: "
    f"{maximum_confidence:.4f}"
)


# ============================================================
# ROOT CAUSE × RECOVERY DIRECTION
# ============================================================

print(
    "\nRoot cause → recovery direction:"
)

cross_tab = pd.crosstab(

    results_df[
        "cause_category"
    ],

    results_df[
        "recommended_direction"
    ]
)

print(
    cross_tab
)


# ============================================================
# HIGH-VALUE TRANSACTIONS
# ============================================================

print(
    "\nHigh-value transactions requiring escalation:"
)

high_value = results_df[
    results_df[
        "recommended_direction"
    ] == "escalate"
].sort_values(
    "amount",
    ascending=False
).head(10)


print(
    high_value[
        [
            "transaction_id",
            "amount",
            "failure_reason",
            "attempt_number",
            "root_cause",
            "nature",
            "confidence",
            "recommended_direction",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

output_file = os.path.join(
    DATA_DIR,
    "root_cause_evaluation.csv"
)

results_df.to_csv(
    output_file,
    index=False
)


print(
    f"\nDetailed results saved to:"
    f"\n{output_file}"
)


print(
    "\n=========================================="
)