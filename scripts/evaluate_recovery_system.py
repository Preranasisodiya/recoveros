import os

import pandas as pd

from src.agent.recovery_agent import RecoveryAgent


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

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "recovery_system_evaluation.csv"
)


# ============================================================
# HEADER
# ============================================================

print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery System Evaluation"
)

print(
    "=========================================="
)


# ============================================================
# LOAD DATASETS
# ============================================================

print(
    "\nLoading datasets..."
)

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
        "customer_tenure_days",
        "historical_success_rate",
        "avg_transaction_amount",
    ]
].copy()


# ============================================================
# PREPARE PAYMENT ATTEMPT FEATURES
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
)


# ============================================================
# KEEP FAILED TRANSACTIONS ONLY
# ============================================================

dataset = dataset[
    dataset["status"] == "failed"
].copy()


print(
    f"\nFailed transactions: "
    f"{len(dataset):,}"
)


# ============================================================
# VALIDATE REQUIRED FEATURES
# ============================================================

required_features = [

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


missing_features = [
    feature
    for feature in required_features
    if feature not in dataset.columns
]


if missing_features:

    raise ValueError(
        "Required evaluation features missing: "
        + ", ".join(missing_features)
    )


# ============================================================
# INITIALIZE RECOVERY AGENT
# ============================================================

print(
    "\nInitializing Recovery Agent..."
)

agent = RecoveryAgent()


# ============================================================
# PROCESS TRANSACTIONS
# ============================================================

print(
    "\nProcessing failed transactions..."
)


results = []


total_transactions = len(
    dataset
)


for index, row in dataset.iterrows():

    transaction = {

        "transaction_id":
            row["transaction_id"],

        "amount":
            float(row["amount"]),

        "status":
            row["status"],

        "failure_reason":
            row["failure_reason"],

        "payment_method":
            row["payment_method"],

        "attempt_number":
            int(row["attempt_number"]),

        "historical_success_rate":
            float(
                row[
                    "historical_success_rate"
                ]
            ),

        "customer_tenure_days":
            int(
                row[
                    "customer_tenure_days"
                ]
            ),

        "avg_transaction_amount":
            float(
                row[
                    "avg_transaction_amount"
                ]
            ),

        "transaction_hour":
            int(
                row["transaction_hour"]
            ),

        "bank":
            row["bank"],

        "checkout_completed":
            bool(
                row[
                    "checkout_completed"
                ]
            ),

        "subscription_flag":
            bool(
                row[
                    "subscription_flag"
                ]
            ),
    }


    # --------------------------------------------------------
    # ANALYZE TRANSACTION
    # --------------------------------------------------------

    state = agent.process(
        transaction
    )


    # --------------------------------------------------------
    # EXECUTE SIMULATED RECOVERY
    #
    # The RecoverySimulator itself determines the outcome
    # deterministically from recovery probability when no
    # forced outcome is supplied.
    # --------------------------------------------------------

    state = agent.execute_recovery(
        state
    )


    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append({

        "transaction_id":
            state.transaction_id,

        "amount":
            state.amount,

        "failure_reason":
            state.failure_reason,

        "attempt_number":
            state.attempt_number,

        "risk_score":
            state.risk_score,

        "risk_level":
            state.risk_level,

        "root_cause":
            state.root_cause,

        "cause_category":
            state.cause_category,

        "cause_nature":
            state.cause_nature,

        "root_cause_confidence":
            state.root_cause_confidence,

        "recovery_direction":
            state.recovery_direction,

        "recovery_probability":
            state.recovery_probability,

        "decision":
            state.decision,

        "decision_confidence":
            state.decision_confidence,

        "status":
            state.status,

        "recovered_amount":
            state.recovered_amount,

        "escalation_required":
            state.escalation_required,

        "escalation_reason":
            state.escalation_reason,

        "action_count":
            len(
                state.actions_taken
            ),
    })


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    processed = len(results)

    if processed % 500 == 0:

        print(
            f"Processed "
            f"{processed:,}/"
            f"{total_transactions:,}"
        )


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)


# ============================================================
# REVENUE AT RISK
# ============================================================

total_failed_revenue = (
    results_df[
        "amount"
    ].sum()
)


# ============================================================
# AUTOMATED RECOVERY DECISIONS
# ============================================================

automated_recovery_decisions = {

    "retry_now",

    "retry_later",

    "alternate_payment",

    "send_reminder",
}


eligible_results = results_df[
    results_df[
        "decision"
    ].isin(
        automated_recovery_decisions
    )
]


eligible_revenue = (
    eligible_results[
        "amount"
    ].sum()
)


# ============================================================
# RECOVERED REVENUE
# ============================================================

recovered_revenue = (
    results_df[
        "recovered_amount"
    ].sum()
)


# ============================================================
# RECOVERY RATE
# ============================================================

if eligible_revenue > 0:

    recovery_rate = (
        recovered_revenue
        / eligible_revenue
    )

else:

    recovery_rate = 0.0


# ============================================================
# DECISION DISTRIBUTION
# ============================================================

decision_distribution = (
    results_df[
        "decision"
    ]
    .value_counts()
)


# ============================================================
# REVENUE BY DECISION
# ============================================================

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


# ============================================================
# RECOVERED REVENUE BY DECISION
# ============================================================

recovered_by_decision = (
    results_df
    .groupby(
        "decision"
    )[
        "recovered_amount"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
)


# ============================================================
# FINAL STATUS DISTRIBUTION
# ============================================================

status_distribution = (
    results_df[
        "status"
    ]
    .value_counts()
)


# ============================================================
# ESCALATION METRICS
# ============================================================

escalated_results = results_df[
    results_df[
        "status"
    ] == "escalated"
]


escalated_count = len(
    escalated_results
)


escalated_revenue = (
    escalated_results[
        "amount"
    ].sum()
)


# ============================================================
# PRINT SUMMARY
# ============================================================

print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery System Results"
)

print(
    "=========================================="
)


print(
    f"\nFailed transactions evaluated: "
    f"{len(results_df):,}"
)


print(
    f"Failed-payment revenue: "
    f"₹{total_failed_revenue:,.2f}"
)


print(
    f"Revenue associated with automated "
    f"recovery decisions: "
    f"₹{eligible_revenue:,.2f}"
)


print(
    f"Simulated recovered revenue: "
    f"₹{recovered_revenue:,.2f}"
)


print(
    f"Simulated recovery rate: "
    f"{recovery_rate:.2%}"
)


# ============================================================
# DECISION DISTRIBUTION
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Decision distribution"
)

print(
    "------------------------------------------"
)


print(
    decision_distribution
)


# ============================================================
# REVENUE BY DECISION
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Revenue by decision"
)

print(
    "------------------------------------------"
)


for decision, revenue in (
    revenue_by_decision.items()
):

    print(
        f"{decision}: "
        f"₹{revenue:,.2f}"
    )


# ============================================================
# RECOVERED REVENUE BY DECISION
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Recovered revenue by decision"
)

print(
    "------------------------------------------"
)


for decision, revenue in (
    recovered_by_decision.items()
):

    print(
        f"{decision}: "
        f"₹{revenue:,.2f}"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Final recovery status"
)

print(
    "------------------------------------------"
)


print(
    status_distribution
)


# ============================================================
# ESCALATION SUMMARY
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Escalation summary"
)

print(
    "------------------------------------------"
)


print(
    f"Escalated transactions: "
    f"{escalated_count:,}"
)


print(
    f"Revenue requiring manual control: "
    f"₹{escalated_revenue:,.2f}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\n=========================================="
)

print(
    "Detailed results saved to:"
)

print(
    OUTPUT_FILE
)

print(
    "==========================================\n"
)