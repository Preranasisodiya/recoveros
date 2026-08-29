import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RecoverOS",
    page_icon="\U0001F4B3",
    layout="wide",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_api_data(endpoint):

    try:

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:

        st.error(
            f"Unable to connect to RecoverOS API: {exc}"
        )

        return None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">RecoverOS</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Revenue Recovery Intelligence Platform'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# API HEALTH CHECK
# ============================================================

health = get_api_data("/health")

if health:

    st.success(
        "RecoverOS API is online"
    )

else:

    st.error(
        "RecoverOS API is unavailable. "
        "Make sure Uvicorn is running."
    )

    st.stop()


# ============================================================
# LOAD BUSINESS METRICS
# ============================================================

metrics_response = get_api_data(
    "/metrics"
)

if not metrics_response:
    st.stop()

metrics = metrics_response.get(
    "metrics",
    {}
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader(
    "Business Overview"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Failed Transactions",
        f"{int(metrics.get('failed_transactions', 0)):,}",
    )


with col2:

    st.metric(
        "Failed-Payment Revenue",
        f"\u20B9{metrics.get('failed_payment_revenue', 0):,.2f}",
    )


with col3:

    st.metric(
        "Recovered Revenue",
        f"\u20B9{metrics.get('simulated_recovered_revenue', 0):,.2f}",
    )


with col4:

    recovery_rate = (
        metrics.get(
            "overall_simulated_recovery_rate",
            0
        )
        * 100
    )

    st.metric(
        "Overall Recovery Rate",
        f"{recovery_rate:.2f}%",
    )


# ============================================================
# SECONDARY METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Automated Recovery Revenue",
        f"\u20B9{metrics.get('automated_recovery_revenue', 0):,.2f}",
    )


with col2:

    automated_rate = (
        metrics.get(
            "automated_recovery_rate",
            0
        )
        * 100
    )

    st.metric(
        "Automated Recovery Rate",
        f"{automated_rate:.2f}%",
    )


with col3:

    st.metric(
        "Unrecovered Revenue",
        f"\u20B9{metrics.get('unrecovered_revenue', 0):,.2f}",
    )


with col4:

    st.metric(
        "Escalated Transactions",
        f"{int(metrics.get('escalated_transactions', 0)):,}",
    )


st.divider()


# ============================================================
# LOAD TRANSACTION DATA
# ============================================================

transactions_response = get_api_data(
    "/transactions"
)

if not transactions_response:
    st.stop()

transactions = transactions_response.get(
    "transactions",
    []
)

transactions_df = pd.DataFrame(
    transactions
)


# ============================================================
# BUSINESS IMPACT ANALYSIS
# ============================================================

st.subheader(
    "Business Impact Analysis"
)

if not transactions_df.empty:

    # --------------------------------------------------------
    # Prepare revenue columns
    # --------------------------------------------------------

    transactions_df[
        "recovered_amount"
    ] = pd.to_numeric(
        transactions_df[
            "recovered_amount"
        ],
        errors="coerce"
    ).fillna(0)

    transactions_df[
        "amount"
    ] = pd.to_numeric(
        transactions_df[
            "amount"
        ],
        errors="coerce"
    ).fillna(0)

    transactions_df[
        "recovery_probability"
    ] = pd.to_numeric(
        transactions_df[
            "recovery_probability"
        ],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Decision-level analysis
    # --------------------------------------------------------

    decision_summary = (
        transactions_df
        .groupby("decision")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            revenue=(
                "amount",
                "sum"
            ),
            recovered=(
                "recovered_amount",
                "sum"
            ),
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    decision_summary[
        "recovery_rate"
    ] = (
        decision_summary["recovered"]
        / decision_summary["revenue"]
        .replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Risk-level analysis
    # --------------------------------------------------------

    risk_summary = (
        transactions_df
        .groupby("risk_level")
        .agg(
            transactions=(
                "transaction_id",
                "count"
            ),
            revenue=(
                "amount",
                "sum"
            ),
            recovered=(
                "recovered_amount",
                "sum"
            ),
        )
    )

    risk_summary[
        "recovery_rate"
    ] = (
        risk_summary["recovered"]
        / risk_summary["revenue"]
        .replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Root-cause analysis
    # --------------------------------------------------------

    root_cause_summary = (
        transactions_df
        .groupby("root_cause")
        .agg(
            revenue=(
                "amount",
                "sum"
            ),
            recovered=(
                "recovered_amount",
                "sum"
            ),
        )
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(6)
    )

    root_cause_summary[
        "recovery_rate"
    ] = (
        root_cause_summary["recovered"]
        / root_cause_summary["revenue"]
        .replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Charts
    # --------------------------------------------------------

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.markdown(
            "**Revenue by Recovery Decision**"
        )

        st.bar_chart(
            decision_summary[
                "revenue"
            ]
        )

    with chart_col2:

        st.markdown(
            "**Recovery Rate by Risk Level**"
        )

        risk_chart = (
            risk_summary[
                "recovery_rate"
            ] * 100
        )

        st.bar_chart(
            risk_chart
        )

    # --------------------------------------------------------
    # Root cause revenue chart
    # --------------------------------------------------------

    st.markdown(
        "**Top Root Causes by Revenue**"
    )

    st.bar_chart(
        root_cause_summary[
            "revenue"
        ]
    )

    # --------------------------------------------------------
    # Business impact table
    # --------------------------------------------------------

    st.markdown(
        "**Business Impact by Decision**"
    )

    business_table = decision_summary.copy()

    business_table[
        "recovery_rate"
    ] = (
        business_table[
            "recovery_rate"
        ] * 100
    ).round(2)

    business_table[
        "revenue"
    ] = business_table[
        "revenue"
    ].round(2)

    business_table[
        "recovered"
    ] = business_table[
        "recovered"
    ].round(2)

    business_table = (
        business_table
        .rename(
            columns={
                "transactions":
                    "Transactions",
                "revenue":
                    "Revenue",
                "recovered":
                    "Recovered Revenue",
                "recovery_rate":
                    "Recovery Rate (%)",
            }
        )
    )

    st.dataframe(
        business_table,
        use_container_width=True,
    )

else:

    st.info(
        "No transaction data available."
    )


st.divider()


# ============================================================
# RECOVERY DECISION DISTRIBUTION
# ============================================================

st.subheader(
    "Recovery Decision Distribution"
)

if not transactions_df.empty:

    decision_counts = (
        transactions_df[
            "decision"
        ]
        .value_counts()
    )

    st.bar_chart(
        decision_counts
    )


st.divider()

# ============================================================
# TRANSACTION INVESTIGATION
# ============================================================

st.divider()

st.subheader(
    "Transaction Investigation"
)

if not transactions_df.empty:

    selected_transaction_id = st.selectbox(
        "Select a transaction",
        transactions_df["transaction_id"].tolist(),
    )

    selected_transaction = transactions_df[
        transactions_df["transaction_id"]
        == selected_transaction_id
    ].iloc[0]

    # --------------------------------------------------------
    # BASIC TRANSACTION INFORMATION
    # --------------------------------------------------------

    st.markdown("### Transaction Details")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Transaction Amount",
            f"₹{selected_transaction['amount']:,.2f}",
        )

    with col2:
        st.metric(
            "Risk Level",
            selected_transaction["risk_level"],
        )

    with col3:
        st.metric(
            "Recovery Probability",
            f"{selected_transaction['recovery_probability'] * 100:.2f}%",
        )

    with col4:
        st.metric(
            "Recovered Amount",
            f"₹{selected_transaction['recovered_amount']:,.2f}",
        )

    # --------------------------------------------------------
    # RECOVERY ANALYSIS
    # --------------------------------------------------------

    st.markdown("### Recovery Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Failure Reason:**",
            selected_transaction["failure_reason"],
        )

        st.write(
            "**Root Cause:**",
            selected_transaction["root_cause"],
        )

        st.write(
            "**Cause Category:**",
            selected_transaction["cause_category"],
        )

        st.write(
            "**Cause Nature:**",
            selected_transaction["cause_nature"],
        )

        st.write(
            "**Root Cause Confidence:**",
            f"{selected_transaction['root_cause_confidence'] * 100:.2f}%",
        )

    with col2:

        st.write(
            "**Recovery Direction:**",
            selected_transaction["recovery_direction"],
        )

        st.write(
            "**Decision:**",
            selected_transaction["decision"],
        )

        st.write(
            "**Decision Confidence:**",
            f"{selected_transaction['decision_confidence'] * 100:.2f}%",
        )

        st.write(
            "**Final Status:**",
            selected_transaction["status"],
        )

        st.write(
            "**Escalation Required:**",
            str(selected_transaction["escalation_required"]),
        )

    # --------------------------------------------------------
    # RECOVERY JOURNEY
    # --------------------------------------------------------

    st.markdown("### Recovery Journey")

    journey = pd.DataFrame(
        {
            "Stage": [
                "Risk Assessment",
                "Root Cause Analysis",
                "Recovery Prediction",
                "Decision",
                "Recovery Outcome",
            ],
            "Result": [
                selected_transaction["risk_level"],
                selected_transaction["root_cause"],
                f"{selected_transaction['recovery_probability'] * 100:.2f}%",
                selected_transaction["decision"],
                selected_transaction["status"],
            ],
        }
    )

    st.dataframe(
        journey,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# TRANSACTION TABLE
# ============================================================

st.subheader(
    "Recovery Transactions"
)

if not transactions_df.empty:

    display_columns = [
        "transaction_id",
        "amount",
        "risk_level",
        "root_cause",
        "recovery_probability",
        "decision",
        "status",
        "recovered_amount",
    ]

    display_df = transactions_df[
        display_columns
    ].copy()

    display_df[
        "recovery_probability"
    ] = (
        display_df[
            "recovery_probability"
        ] * 100
    ).round(2)

    display_df = display_df.rename(
        columns={
            "transaction_id":
                "Transaction",
            "amount":
                "Amount",
            "risk_level":
                "Risk",
            "root_cause":
                "Root Cause",
            "recovery_probability":
                "Recovery Probability (%)",
            "decision":
                "Decision",
            "status":
                "Status",
            "recovered_amount":
                "Recovered Amount",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
    )

else:

    st.info(
        "No transaction data available."
    )

# ============================================================
# LIVE RECOVERY SIMULATOR
# ============================================================

st.divider()

st.subheader(
    "Live Recovery Simulator"
)

st.write(
    "Run a recovery decision for a new failed payment "
    "using the RecoverOS API."
)

col1, col2 = st.columns(2)

with col1:

    transaction_id = st.text_input(
        "Transaction ID",
        value="TXN_DASHBOARD_DEMO",
    )

    amount = st.number_input(
        "Transaction Amount (₹)",
        min_value=1.0,
        value=7499.0,
        step=100.0,
    )

    failure_reason = st.selectbox(
        "Failure Reason",
        [
            "bank_timeout",
            "network_error",
            "insufficient_funds",
            "bank_declined",
            "authentication_failed",
            "expired_card",
        ],
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "credit_card",
            "debit_card",
            "upi",
            "net_banking",
        ],
    )

with col2:

    attempt_number = st.number_input(
        "Attempt Number",
        min_value=1,
        value=1,
        step=1,
    )

    historical_success_rate = st.number_input(
        "Historical Success Rate",
        min_value=0.0,
        max_value=1.0,
        value=0.91,
        step=0.01,
    )

    customer_tenure_days = st.number_input(
        "Customer Tenure (days)",
        min_value=0,
        value=850,
        step=10,
    )

    avg_transaction_amount = st.number_input(
        "Average Transaction Amount (₹)",
        min_value=0.0,
        value=4200.0,
        step=100.0,
    )

transaction_hour = st.slider(
    "Transaction Hour",
    min_value=0,
    max_value=23,
    value=14,
)

bank = st.text_input(
    "Bank",
    value="HDFC",
)

checkout_completed = st.checkbox(
    "Checkout Completed",
    value=True,
)

subscription_flag = st.checkbox(
    "Subscription Transaction",
    value=False,
)

if st.button(
    "Run Recovery Decision",
    type="primary",
):

    payload = {
        "transaction_id": transaction_id,
        "amount": amount,
        "failure_reason": failure_reason,
        "payment_method": payment_method,
        "attempt_number": int(attempt_number),
        "historical_success_rate": historical_success_rate,
        "customer_tenure_days": int(customer_tenure_days),
        "avg_transaction_amount": avg_transaction_amount,
        "transaction_hour": transaction_hour,
        "bank": bank,
        "checkout_completed": checkout_completed,
        "subscription_flag": subscription_flag,
    }

    try:

        response = requests.post(
            f"{API_BASE_URL}/recover",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        st.success(
            "Recovery decision completed."
        )

        st.markdown(
            "### Recovery Result"
        )

        result_col1, result_col2, result_col3, result_col4 = (
            st.columns(4)
        )

        with result_col1:

            st.metric(
                "Risk Level",
                result.get(
                    "risk_level",
                    "N/A",
                ),
            )

        with result_col2:

            probability = (
                result.get(
                    "recovery_probability",
                    0,
                )
                * 100
            )

            st.metric(
                "Recovery Probability",
                f"{probability:.2f}%",
            )

        with result_col3:

            st.metric(
                "Decision",
                result.get(
                    "decision",
                    "N/A",
                ),
            )

        with result_col4:

            st.metric(
                "Status",
                result.get(
                    "status",
                    "N/A",
                ),
            )

        st.markdown(
            "### Recovery Details"
        )

        details = {
            "Transaction ID":
                result.get("transaction_id"),

            "Amount":
                f"₹{result.get('amount', 0):,.2f}",

            "Failure Reason":
                result.get("failure_reason"),

            "Root Cause":
                result.get("root_cause"),

            "Recovery Direction":
                result.get("recovery_direction"),

            "Decision Confidence":
                f"{result.get('decision_confidence', 0) * 100:.2f}%",

            "Recovered Amount":
                f"₹{result.get('recovered_amount', 0):,.2f}",

            "Escalation Required":
                result.get("escalation_required"),

            "Escalation Reason":
                result.get("escalation_reason"),
        }

        details_df = pd.DataFrame(
            list(details.items()),
            columns=[
                "Field",
                "Value",
            ],
        )

        st.dataframe(
            details_df,
            use_container_width=True,
            hide_index=True,
        )

        if result.get(
            "escalation_required",
            False,
        ):

            st.warning(
                "Safety control triggered: "
                "this transaction requires manual review."
            )

        elif result.get(
            "status"
        ) == "recovered":

            st.success(
                f"₹{result.get('recovered_amount', 0):,.2f} "
                "revenue recovered successfully."
            )

    except requests.exceptions.RequestException as exc:

        st.error(
            f"Recovery API request failed: {exc}"
        )

    except Exception as exc:

        st.error(
            f"Unable to process recovery result: {exc}"
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "RecoverOS — Intelligent payment recovery "
    "with risk-aware automation and safety controls."
)