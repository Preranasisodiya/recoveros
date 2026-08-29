import requests
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="RecoverOS",
    page_icon="💳",
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
# LOAD METRICS
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
        f"₹{metrics.get('failed_payment_revenue', 0):,.2f}",
    )


with col3:

    st.metric(
        "Recovered Revenue",
        f"₹{metrics.get('simulated_recovered_revenue', 0):,.2f}",
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


st.divider()


# ============================================================
# SECONDARY METRICS
# ============================================================



col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Automated Recovery Revenue",
        f"₹{metrics.get('automated_recovery_revenue', 0):,.2f}",
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
        f"₹{metrics.get('unrecovered_revenue', 0):,.2f}",
    )


with col4:

    st.metric(
        "Escalated Transactions",
        f"{int(metrics.get('escalated_transactions', 0)):,}",
    )


st.divider()


# ============================================================
# TRANSACTION DATA
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
# DECISION DISTRIBUTION
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
            "transaction_id": "Transaction",
            "amount": "Amount",
            "risk_level": "Risk",
            "root_cause": "Root Cause",
            "recovery_probability":
                "Recovery Probability (%)",
            "decision": "Decision",
            "status": "Status",
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
# FOOTER
# ============================================================

st.divider()

st.caption(
    "RecoverOS — Intelligent payment recovery "
    "with risk-aware automation and safety controls."
)