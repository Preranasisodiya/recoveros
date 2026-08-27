import os

import pandas as pd

from src.risk.revenue_risk_detector import (
    RevenueRiskDetector
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
# PREPARE CUSTOMER DATA
# ============================================================

customer_features = customers_df[
    [
        "customer_id",
        "historical_success_rate",
    ]
].copy()


# ============================================================
# PREPARE ATTEMPT DATA
# ============================================================

# The maximum attempt number represents how many payment
# attempts were made for that transaction.

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
# CREATE DETECTOR
# ============================================================

detector = RevenueRiskDetector()


# ============================================================
# RUN DETECTOR
# ============================================================

results = []


for _, row in failed_df.iterrows():

    transaction = {

        "transaction_id":
            row["transaction_id"],

        "amount":
            row["amount"],

        "status":
            row["status"],

        "failure_reason":
            row["failure_reason"],

        "payment_method":
            row["payment_method"],

        "attempt_number":
            row["attempt_number"],

        "historical_success_rate":
            row[
                "historical_success_rate"
            ],

        "checkout_completed":
            row["checkout_completed"],
    }

    result = detector.detect(
        transaction
    )

    results.append({

        "transaction_id":
            result["transaction_id"],

        "amount":
            row["amount"],

        "failure_reason":
            row["failure_reason"],

        "payment_method":
            row["payment_method"],

        "attempt_number":
            row["attempt_number"],

        "historical_success_rate":
            row[
                "historical_success_rate"
            ],

        "risk_score":
            result["risk_score"],

        "risk_level":
            result["risk_level"],

        "revenue_at_risk":
            result[
                "revenue_at_risk"
            ],

        "recovery_eligible":
            result[
                "recovery_eligible"
            ],
    })


results_df = pd.DataFrame(
    results
)


# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("RecoverOS Revenue Risk Detector Evaluation")
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
# RISK DISTRIBUTION
# ============================================================

print("\nRisk level distribution:")

risk_distribution = (
    results_df[
        "risk_level"
    ]
    .value_counts()
)

print(
    risk_distribution
)


# ============================================================
# RISK PERCENTAGES
# ============================================================

print("\nRisk level percentages:")

risk_percentages = (
    results_df[
        "risk_level"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)

for level, percentage in (
    risk_percentages.items()
):

    print(
        f"{level}: "
        f"{percentage:.2f}%"
    )


# ============================================================
# RECOVERY ELIGIBILITY
# ============================================================

eligible_count = (
    results_df[
        "recovery_eligible"
    ]
    .sum()
)

eligible_percentage = (

    eligible_count
    /
    len(results_df)
    * 100
)


print("\nRecovery eligibility:")

print(
    f"Eligible: "
    f"{eligible_count:,}"
)

print(
    f"Not eligible: "
    f"{len(results_df) - eligible_count:,}"
)

print(
    f"Eligibility rate: "
    f"{eligible_percentage:.2f}%"
)


# ============================================================
# REVENUE AT RISK
# ============================================================

total_revenue_at_risk = (
    results_df[
        "revenue_at_risk"
    ].sum()
)


print("\nRevenue at risk:")

print(
    f"₹{total_revenue_at_risk:,.2f}"
)


# ============================================================
# REVENUE AT RISK BY LEVEL
# ============================================================

print(
    "\nRevenue at risk by risk level:"
)

revenue_by_level = (
    results_df
    .groupby(
        "risk_level"
    )[
        "revenue_at_risk"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
)

for level, amount in (
    revenue_by_level.items()
):

    print(
        f"{level}: "
        f"₹{amount:,.2f}"
    )


# ============================================================
# AVERAGE RISK SCORE
# ============================================================

average_risk_score = (
    results_df[
        "risk_score"
    ].mean()
)


print(
    "\nAverage risk score: "
    f"{average_risk_score:.4f}"
)


# ============================================================
# TOP 10 HIGH-RISK TRANSACTIONS
# ============================================================

print(
    "\nTop 10 highest-risk transactions:"
)

top_risk = (
    results_df
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)

print(
    top_risk[
        [
            "transaction_id",
            "amount",
            "failure_reason",
            "attempt_number",
            "risk_score",
            "risk_level",
            "recovery_eligible",
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
    "risk_evaluation.csv"
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