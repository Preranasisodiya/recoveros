import os

import pandas as pd

from src.risk.revenue_risk_detector import (
    RevenueRiskDetector
)

from src.root_cause.root_cause_engine import (
    RootCauseEngine
)

from src.ml.recovery_model import (
    RecoveryProbabilityModel
)

from src.decision.decision_engine import (
    DecisionEngine
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

MODEL_FILE = (
    "models/recovery_probability_model.joblib"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "decision_evaluation.csv"
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


# ============================================================
# PREPARE CUSTOMER DATA
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
# PREPARE ATTEMPT DATA
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
# CREATE COMPONENTS
# ============================================================

risk_detector = RevenueRiskDetector()

root_cause_engine = RootCauseEngine()

recovery_model = RecoveryProbabilityModel()

decision_engine = DecisionEngine()


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

print(
    "\nLoading trained recovery model..."
)

recovery_model.load(
    MODEL_FILE
)


# ============================================================
# RUN COMPLETE DECISION PIPELINE
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


    # ========================================================
    # RISK
    # ========================================================

    risk_result = risk_detector.detect(
        transaction
    )


    # ========================================================
    # ROOT CAUSE
    # ========================================================

    root_result = root_cause_engine.analyze(
        transaction
    )


    # ========================================================
    # ML FEATURES
    # ========================================================

    ml_input = pd.DataFrame([
        {
            "amount":
                row["amount"],

            "attempt_number":
                row["attempt_number"],

            "historical_success_rate":
                row[
                    "historical_success_rate"
                ],

            "customer_tenure_days":
                row[
                    "customer_tenure_days"
                ],

            "avg_transaction_amount":
                row[
                    "avg_transaction_amount"
                ],

            "transaction_hour":
                pd.to_datetime(
                    row["transaction_time"]
                ).hour,

            "payment_method":
                row["payment_method"],

            "bank":
                row["bank"],

            "failure_reason":
                row["failure_reason"],

            "checkout_completed":
                row["checkout_completed"],

            "subscription_flag":
                row["subscription_flag"],
        }
    ])


    # ========================================================
    # RECOVERY PROBABILITY
    # ========================================================

    recovery_probability = (
        recovery_model
        .predict_probability(
            ml_input
        )[0]
    )


    # ========================================================
    # DECISION
    # ========================================================

    decision_result = (
        decision_engine.decide(

            risk_score=
                risk_result[
                    "risk_score"
                ],

            risk_level=
                risk_result[
                    "risk_level"
                ],

            recovery_probability=
                recovery_probability,

            root_cause=
                root_result[
                    "root_cause"
                ],

            recovery_direction=
                root_result[
                    "recommended_direction"
                ],

            attempt_number=
                row["attempt_number"],

            amount=
                row["amount"],
        )
    )


    # ========================================================
    # STORE RESULT
    # ========================================================

    results.append({

        "transaction_id":
            row["transaction_id"],

        "amount":
            row["amount"],

        "failure_reason":
            row["failure_reason"],

        "attempt_number":
            row["attempt_number"],

        "risk_score":
            risk_result[
                "risk_score"
            ],

        "risk_level":
            risk_result[
                "risk_level"
            ],

        "root_cause":
            root_result[
                "root_cause"
            ],

        "cause_category":
            root_result[
                "cause_category"
            ],

        "root_cause_confidence":
            root_result[
                "confidence"
            ],

        "recovery_probability":
            round(
                recovery_probability,
                4
            ),

        "recovery_direction":
            root_result[
                "recommended_direction"
            ],

        "decision":
            decision_result[
                "action"
            ],

        "decision_confidence":
            decision_result[
                "decision_confidence"
            ],

        "decision_reason":
            decision_result[
                "reason"
            ],

    })


results_df = pd.DataFrame(
    results
)


# ============================================================
# HEADER
# ============================================================

print(
    "\n=========================================="
)

print(
    "RecoverOS Decision Engine Evaluation"
)

print(
    "=========================================="
)


print(
    f"\nFailed transactions evaluated: "
    f"{len(results_df):,}"
)


# ============================================================
# DECISION DISTRIBUTION
# ============================================================

print(
    "\nDecision distribution:"
)

decision_distribution = (
    results_df[
        "decision"
    ]
    .value_counts()
)

print(
    decision_distribution
)


# ============================================================
# DECISION PERCENTAGES
# ============================================================

print(
    "\nDecision percentages:"
)

decision_percentages = (
    results_df[
        "decision"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)

for decision, percentage in (
    decision_percentages.items()
):

    print(
        f"{decision}: "
        f"{percentage:.2f}%"
    )


# ============================================================
# REVENUE BY DECISION
# ============================================================

print(
    "\nRevenue associated with each decision:"
)

revenue_by_decision = (
    results_df
    .groupby(
        "decision"
    )[
        "amount"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
)

for decision, amount in (
    revenue_by_decision.items()
):

    print(
        f"{decision}: "
        f"₹{amount:,.2f}"
    )


# ============================================================
# AVERAGE RECOVERY PROBABILITY BY DECISION
# ============================================================

print(
    "\nAverage recovery probability by decision:"
)

probability_by_decision = (
    results_df
    .groupby(
        "decision"
    )[
        "recovery_probability"
    ]
    .mean()
    .sort_values(
        ascending=False
    )
)

for decision, probability in (
    probability_by_decision.items()
):

    print(
        f"{decision}: "
        f"{probability:.2%}"
    )


# ============================================================
# CRITICAL TRANSACTIONS
# ============================================================

print(
    "\nCritical transactions:"
)

critical_df = results_df[
    results_df[
        "risk_level"
    ] == "CRITICAL"
].sort_values(
    "recovery_probability",
    ascending=False
)


print(
    critical_df[
        [
            "transaction_id",
            "amount",
            "failure_reason",
            "risk_score",
            "root_cause",
            "recovery_probability",
            "decision",
        ]
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nDetailed results saved to:"
    f"\n{OUTPUT_FILE}"
)


print(
    "\n=========================================="
)

print(
    "Decision evaluation completed."
)

print(
    "==========================================\n"
)