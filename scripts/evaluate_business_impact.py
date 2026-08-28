import os

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "data"

INPUT_FILE = os.path.join(
    DATA_DIR,
    "recovery_system_evaluation.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "business_impact_summary.csv"
)


# ============================================================
# HEADER
# ============================================================

print(
    "\n=========================================="
)

print(
    "RecoverOS Business Impact Evaluation"
)

print(
    "=========================================="
)


# ============================================================
# LOAD EVALUATION RESULTS
# ============================================================

print(
    "\nLoading recovery system evaluation..."
)

df = pd.read_csv(
    INPUT_FILE
)


print(
    f"Transactions evaluated: "
    f"{len(df):,}"
)


# ============================================================
# TOTAL FAILED-PAYMENT REVENUE
# ============================================================

total_failed_revenue = (
    df["amount"].sum()
)


# ============================================================
# RECOVERED REVENUE
# ============================================================

total_recovered_revenue = (
    df["recovered_amount"].sum()
)


# ============================================================
# UNRECOVERED REVENUE
# ============================================================

unrecovered_revenue = (
    total_failed_revenue
    - total_recovered_revenue
)


# ============================================================
# OVERALL RECOVERY RATE
# ============================================================

if total_failed_revenue > 0:

    overall_recovery_rate = (
        total_recovered_revenue
        / total_failed_revenue
    )

else:

    overall_recovery_rate = 0.0


# ============================================================
# AUTOMATED RECOVERY DECISIONS
# ============================================================

automated_decisions = {

    "retry_now",

    "retry_later",

    "alternate_payment",

    "send_reminder",
}


automated_df = df[
    df["decision"].isin(
        automated_decisions
    )
].copy()


automated_revenue = (
    automated_df["amount"].sum()
)


automated_recovery_rate = (

    total_recovered_revenue
    / automated_revenue

    if automated_revenue > 0

    else 0.0
)


# ============================================================
# DECISION METRICS
# ============================================================

decision_summary = (

    df.groupby("decision")

    .agg(

        transaction_count=(
            "transaction_id",
            "count"
        ),

        revenue=(
            "amount",
            "sum"
        ),

        recovered_revenue=(
            "recovered_amount",
            "sum"
        ),

        average_recovery_probability=(
            "recovery_probability",
            "mean"
        ),
    )

    .reset_index()
)


decision_summary[
    "recovery_rate"
] = (

    decision_summary[
        "recovered_revenue"
    ]

    / decision_summary[
        "revenue"
    ]

).fillna(0)


# ============================================================
# STATUS METRICS
# ============================================================

status_summary = (

    df.groupby("status")

    .agg(

        transaction_count=(
            "transaction_id",
            "count"
        ),

        revenue=(
            "amount",
            "sum"
        ),

        recovered_revenue=(
            "recovered_amount",
            "sum"
        ),
    )

    .reset_index()
)


# ============================================================
# RISK-LEVEL METRICS
# ============================================================

risk_summary = (

    df.groupby("risk_level")

    .agg(

        transaction_count=(
            "transaction_id",
            "count"
        ),

        revenue=(
            "amount",
            "sum"
        ),

        recovered_revenue=(
            "recovered_amount",
            "sum"
        ),

        average_recovery_probability=(
            "recovery_probability",
            "mean"
        ),
    )

    .reset_index()
)


risk_summary[
    "recovery_rate"
] = (

    risk_summary[
        "recovered_revenue"
    ]

    / risk_summary[
        "revenue"
    ]

).fillna(0)


# ============================================================
# ROOT-CAUSE METRICS
# ============================================================

root_cause_summary = (

    df.groupby("root_cause")

    .agg(

        transaction_count=(
            "transaction_id",
            "count"
        ),

        revenue=(
            "amount",
            "sum"
        ),

        recovered_revenue=(
            "recovered_amount",
            "sum"
        ),

        average_recovery_probability=(
            "recovery_probability",
            "mean"
        ),
    )

    .reset_index()
)


root_cause_summary[
    "recovery_rate"
] = (

    root_cause_summary[
        "recovered_revenue"
    ]

    / root_cause_summary[
        "revenue"
    ]

).fillna(0)


# ============================================================
# ESCALATION METRICS
# ============================================================

escalation_df = df[
    df["escalation_required"] == True
]


escalated_transactions = len(
    escalation_df
)


escalated_revenue = (
    escalation_df["amount"].sum()
)


# ============================================================
# HIGH-VALUE SAFETY CHECK
# ============================================================

high_value_df = df[
    df["amount"] > 50000
]


high_value_count = len(
    high_value_df
)


high_value_escalated = len(
    high_value_df[
        high_value_df[
            "decision"
        ] == "escalate"
    ]
)


# ============================================================
# PRINT BUSINESS SUMMARY
# ============================================================

print(
    "\n=========================================="
)

print(
    "Business Impact Summary"
)

print(
    "=========================================="
)


print(
    f"\nFailed transactions: "
    f"{len(df):,}"
)


print(
    f"Failed-payment revenue: "
    f"₹{total_failed_revenue:,.2f}"
)


print(
    f"Revenue exposed to automated "
    f"recovery decisions: "
    f"₹{automated_revenue:,.2f}"
)


print(
    f"Simulated recovered revenue: "
    f"₹{total_recovered_revenue:,.2f}"
)


print(
    f"Unrecovered revenue: "
    f"₹{unrecovered_revenue:,.2f}"
)


print(
    f"Overall simulated recovery rate: "
    f"{overall_recovery_rate:.2%}"
)


print(
    f"Recovery rate on automated "
    f"recovery revenue: "
    f"{automated_recovery_rate:.2%}"
)


# ============================================================
# DECISION BREAKDOWN
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Business impact by decision"
)

print(
    "------------------------------------------"
)


for _, row in decision_summary.iterrows():

    print(
        f"{row['decision']}: "
        f"{int(row['transaction_count']):,} "
        f"transactions | "
        f"Revenue ₹{row['revenue']:,.2f} | "
        f"Recovered ₹{row['recovered_revenue']:,.2f} | "
        f"Recovery rate "
        f"{row['recovery_rate']:.2%}"
    )


# ============================================================
# STATUS BREAKDOWN
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Business impact by final status"
)

print(
    "------------------------------------------"
)


for _, row in status_summary.iterrows():

    print(
        f"{row['status']}: "
        f"{int(row['transaction_count']):,} "
        f"transactions | "
        f"Revenue ₹{row['revenue']:,.2f} | "
        f"Recovered ₹{row['recovered_revenue']:,.2f}"
    )


# ============================================================
# RISK BREAKDOWN
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Business impact by risk level"
)

print(
    "------------------------------------------"
)


for _, row in risk_summary.iterrows():

    print(
        f"{row['risk_level']}: "
        f"{int(row['transaction_count']):,} "
        f"transactions | "
        f"Revenue ₹{row['revenue']:,.2f} | "
        f"Recovered ₹{row['recovered_revenue']:,.2f} | "
        f"Recovery rate "
        f"{row['recovery_rate']:.2%}"
    )


# ============================================================
# ROOT CAUSE BREAKDOWN
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Top root causes by revenue"
)

print(
    "------------------------------------------"
)


root_cause_display = (
    root_cause_summary
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(10)
)


for _, row in (
    root_cause_display.iterrows()
):

    print(
        f"{row['root_cause']}: "
        f"Revenue ₹{row['revenue']:,.2f} | "
        f"Recovered ₹{row['recovered_revenue']:,.2f} | "
        f"Recovery rate "
        f"{row['recovery_rate']:.2%}"
    )


# ============================================================
# ESCALATION / SAFETY
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Safety boundary"
)

print(
    "------------------------------------------"
)


print(
    f"Escalated transactions: "
    f"{escalated_transactions:,}"
)


print(
    f"Revenue requiring manual control: "
    f"₹{escalated_revenue:,.2f}"
)


print(
    f"High-value transactions (>₹50,000): "
    f"{high_value_count:,}"
)


print(
    f"High-value transactions escalated: "
    f"{high_value_escalated:,}"
)


# ============================================================
# CREATE SUMMARY OUTPUT
# ============================================================

summary_rows = [

    {
        "metric":
            "failed_transactions",

        "value":
            len(df),
    },

    {
        "metric":
            "failed_payment_revenue",

        "value":
            total_failed_revenue,
    },

    {
        "metric":
            "automated_recovery_revenue",

        "value":
            automated_revenue,
    },

    {
        "metric":
            "simulated_recovered_revenue",

        "value":
            total_recovered_revenue,
    },

    {
        "metric":
            "unrecovered_revenue",

        "value":
            unrecovered_revenue,
    },

    {
        "metric":
            "overall_simulated_recovery_rate",

        "value":
            overall_recovery_rate,
    },

    {
        "metric":
            "automated_recovery_rate",

        "value":
            automated_recovery_rate,
    },

    {
        "metric":
            "escalated_transactions",

        "value":
            escalated_transactions,
    },

    {
        "metric":
            "escalated_revenue",

        "value":
            escalated_revenue,
    },

    {
        "metric":
            "high_value_transactions",

        "value":
            high_value_count,
    },

    {
        "metric":
            "high_value_transactions_escalated",

        "value":
            high_value_escalated,
    },
]


summary_df = pd.DataFrame(
    summary_rows
)


# ============================================================
# SAVE SUMMARY
# ============================================================

summary_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\n=========================================="
)

print(
    "Business impact summary saved to:"
)

print(
    OUTPUT_FILE
)

print(
    "==========================================\n"
)