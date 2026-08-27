import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

NUM_CUSTOMERS = 2000
NUM_MERCHANTS = 50
NUM_TRANSACTIONS = 10000

random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CONSTANTS
# ============================================================

PAYMENT_METHODS = [
    "UPI",
    "Card",
    "NetBanking",
    "Wallet",
]

BANKS = [
    "HDFC",
    "ICICI",
    "SBI",
    "AXIS",
    "KOTAK",
    "YES",
]

FAILURE_REASONS = [
    "bank_timeout",
    "network_error",
    "authentication_failure",
    "insufficient_funds",
    "expired_card",
    "bank_declined",
]

RESPONSE_CODES = {
    "bank_timeout": "TIMEOUT",
    "network_error": "NETWORK_ERROR",
    "authentication_failure": "AUTH_FAILED",
    "insufficient_funds": "INSUFFICIENT_FUNDS",
    "expired_card": "CARD_EXPIRED",
    "bank_declined": "BANK_DECLINED",
}

RECOVERY_ACTIONS = [
    "retry_now",
    "retry_later",
    "send_reminder",
    "alternate_payment",
    "escalate",
    "stop",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def weighted_choice(items, probabilities=None):
    """Select one item using optional weights."""
    return random.choices(
        items,
        weights=probabilities,
        k=1
    )[0]


def generate_transaction_amount():
    """
    Generate realistic Indian transaction amounts.

    Most transactions are relatively small, with a smaller
    number of high-value transactions.
    """

    amount = np.random.lognormal(
        mean=7.8,
        sigma=0.8
    )

    amount = max(
        100,
        min(amount, 100000)
    )

    return round(amount, 2)


def choose_payment_method():
    """Generate payment method using realistic proportions."""

    return weighted_choice(
        PAYMENT_METHODS,
        [0.50, 0.30, 0.12, 0.08]
    )


def choose_failure_reason(payment_method):
    """
    Generate a failure reason based on payment method.
    Different payment methods have slightly different
    failure patterns.
    """

    if payment_method == "UPI":

        reasons = [
            "bank_timeout",
            "network_error",
            "bank_declined",
            "authentication_failure",
        ]

        weights = [
            0.35,
            0.25,
            0.25,
            0.15,
        ]

    elif payment_method == "Card":

        reasons = [
            "authentication_failure",
            "insufficient_funds",
            "expired_card",
            "bank_declined",
            "network_error",
        ]

        weights = [
            0.20,
            0.25,
            0.15,
            0.25,
            0.15,
        ]

    elif payment_method == "NetBanking":

        reasons = [
            "bank_timeout",
            "network_error",
            "bank_declined",
            "authentication_failure",
        ]

        weights = [
            0.35,
            0.25,
            0.25,
            0.15,
        ]

    else:

        reasons = [
            "bank_timeout",
            "network_error",
            "bank_declined",
            "insufficient_funds",
        ]

        weights = [
            0.30,
            0.25,
            0.25,
            0.20,
        ]

    return weighted_choice(
        reasons,
        weights
    )


def calculate_recovery_probability(
    failure_reason,
    historical_success_rate,
    attempt_number,
    payment_method,
    bank_degradation=False,
):
    """
    Generate the synthetic ground-truth recovery probability.

    This represents the underlying behavior of our simulated
    payment system.

    Later, the ML model will try to learn these relationships
    using only information available before recovery.
    """

    probability = 0.50

    # --------------------------------------------------------
    # Customer history
    # --------------------------------------------------------

    probability += (
        historical_success_rate - 0.50
    ) * 0.50

    # --------------------------------------------------------
    # Failure reason
    # --------------------------------------------------------

    reason_effect = {

        # Usually temporary and recoverable
        "bank_timeout": 0.22,

        "network_error": 0.18,

        # Moderate difficulty
        "authentication_failure": -0.05,

        # More difficult
        "insufficient_funds": -0.18,

        # Usually requires another payment method
        "expired_card": -0.30,

        "bank_declined": -0.12,
    }

    probability += reason_effect[
        failure_reason
    ]

    # --------------------------------------------------------
    # Previous attempts
    # --------------------------------------------------------

    probability -= (
        max(0, attempt_number - 1) * 0.12
    )

    # --------------------------------------------------------
    # Temporary bank degradation
    # --------------------------------------------------------

    if bank_degradation:
        probability += 0.05

    # --------------------------------------------------------
    # Payment method effect
    # --------------------------------------------------------

    if payment_method == "UPI":
        probability += 0.03

    elif payment_method == "Card":
        probability += 0.01

    # --------------------------------------------------------
    # Natural variation
    # --------------------------------------------------------

    probability += np.random.normal(
        0,
        0.04
    )

    return float(
        np.clip(
            probability,
            0.03,
            0.97
        )
    )


def choose_recovery_action(
    recovery_probability,
    failure_reason,
    attempt_number,
    amount,
):
    """
    Ground-truth recovery policy used to create synthetic
    recovery outcomes.

    The policy supports all six recovery actions:

        retry_now
        retry_later
        send_reminder
        alternate_payment
        escalate
        stop
    """

    # --------------------------------------------------------
    # High-value transactions require human approval.
    # --------------------------------------------------------

    if amount > 50000:
        return "escalate"

    # --------------------------------------------------------
    # Maximum automated attempts reached.
    # --------------------------------------------------------

    if attempt_number >= 3:
        return "stop"

    # --------------------------------------------------------
    # Very low recovery probability.
    # --------------------------------------------------------

    if recovery_probability < 0.20:

        if failure_reason in [
            "expired_card",
            "insufficient_funds",
        ]:
            return "alternate_payment"

        return "stop"

    # --------------------------------------------------------
    # Expired card should not simply be retried.
    # --------------------------------------------------------

    if failure_reason == "expired_card":
        return "alternate_payment"

    # --------------------------------------------------------
    # Very strong recovery opportunity.
    # --------------------------------------------------------

    if recovery_probability >= 0.85:

        if failure_reason in [
            "bank_timeout",
            "network_error",
        ]:
            return "retry_now"

        return "retry_later"

    # --------------------------------------------------------
    # Strong but not immediate recovery opportunity.
    # --------------------------------------------------------

    if recovery_probability >= 0.70:

        if failure_reason in [
            "bank_timeout",
            "network_error",
        ]:
            return "retry_later"

        return "send_reminder"

    # --------------------------------------------------------
    # Medium recovery probability.
    # --------------------------------------------------------

    if recovery_probability >= 0.45:

        if failure_reason in [
            "insufficient_funds",
            "authentication_failure",
        ]:
            return "send_reminder"

        return "retry_later"

    # --------------------------------------------------------
    # Low recovery probability.
    # --------------------------------------------------------

    return "escalate"


def simulate_recovery(
    recovery_probability,
    action,
):
    """
    Simulate whether the selected recovery action succeeds.

    The action modifies the underlying recovery probability
    because different interventions have different effectiveness.
    """

    action_multiplier = {

        "retry_now": 0.90,

        "retry_later": 1.05,

        "send_reminder": 0.75,

        "alternate_payment": 0.85,

        "escalate": 1.10,

        "stop": 0.0,
    }

    adjusted_probability = (
        recovery_probability
        * action_multiplier[action]
    )

    adjusted_probability = float(
        np.clip(
            adjusted_probability,
            0.0,
            0.97
        )
    )

    recovered = (
        random.random()
        < adjusted_probability
    )

    return recovered


# ============================================================
# 1. GENERATE CUSTOMERS
# ============================================================

customers = []

payment_method_preferences = [
    "UPI",
    "Card",
    "NetBanking",
    "Wallet",
]


for i in range(
    1,
    NUM_CUSTOMERS + 1
):

    customer_id = (
        f"CUST_{i:05d}"
    )

    tenure_days = random.randint(
        30,
        1500
    )

    total_transactions = random.randint(
        5,
        80
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Generate transaction counts FIRST.
    # Success rate is derived from the counts.
    # This prevents internal inconsistency.
    # --------------------------------------------------------

    successful_transactions = random.randint(
        max(
            1,
            int(total_transactions * 0.30)
        ),
        total_transactions
    )

    failed_transactions = (
        total_transactions
        - successful_transactions
    )

    historical_success_rate = (
        successful_transactions
        / total_transactions
    )

    avg_transaction_amount = round(
        np.random.lognormal(
            mean=7.7,
            sigma=0.7
        ),
        2
    )

    avg_transaction_amount = max(
        100,
        min(
            avg_transaction_amount,
            75000
        )
    )

    preferred_payment_method = random.choice(
        payment_method_preferences
    )

    customers.append({

        "customer_id":
            customer_id,

        "customer_tenure_days":
            tenure_days,

        "total_transactions":
            total_transactions,

        "successful_transactions":
            successful_transactions,

        "failed_transactions":
            failed_transactions,

        "historical_success_rate":
            round(
                historical_success_rate,
                4
            ),

        "avg_transaction_amount":
            avg_transaction_amount,

        "preferred_payment_method":
            preferred_payment_method,
    })


customers_df = pd.DataFrame(
    customers
)


# ============================================================
# 2. GENERATE TRANSACTIONS
# ============================================================

transactions = []

payment_attempts = []

recovery_outcomes = []

start_date = datetime(
    2026,
    7,
    1
)

transaction_counter = 1

attempt_counter = 1


for _ in range(
    NUM_TRANSACTIONS
):

    transaction_id = (
        f"TXN_{transaction_counter:06d}"
    )

    # --------------------------------------------------------
    # Select customer.
    # --------------------------------------------------------

    customer = customers_df.sample(
        n=1,
        random_state=random.randint(
            0,
            1_000_000
        )
    ).iloc[0]

    customer_id = (
        customer["customer_id"]
    )

    merchant_id = (
        f"MER_{random.randint(1, NUM_MERCHANTS):04d}"
    )

    amount = (
        generate_transaction_amount()
    )

    payment_method = (
        choose_payment_method()
    )

    bank = random.choice(
        BANKS
    )

    transaction_time = (
        start_date
        + timedelta(
            days=random.randint(
                0,
                56
            ),
            minutes=random.randint(
                0,
                1439
            ),
        )
    )

    # --------------------------------------------------------
    # Approximately 30% of transactions fail.
    # --------------------------------------------------------

    is_failed = (
        random.random()
        < 0.30
    )

    if is_failed:

        status = "failed"

        failure_reason = (
            choose_failure_reason(
                payment_method
            )
        )

        checkout_completed = (
            random.random()
            < 0.85
        )

    else:

        status = "success"

        failure_reason = None

        checkout_completed = True

    subscription_flag = (
        random.random()
        < 0.20
    )

    transactions.append({

        "transaction_id":
            transaction_id,

        "customer_id":
            customer_id,

        "merchant_id":
            merchant_id,

        "amount":
            amount,

        "currency":
            "INR",

        "payment_method":
            payment_method,

        "bank":
            bank,

        "transaction_time":
            transaction_time,

        "status":
            status,

        "failure_reason":
            failure_reason,

        "checkout_completed":
            checkout_completed,

        "subscription_flag":
            subscription_flag,
    })

    # --------------------------------------------------------
    # Successful transactions do not require recovery.
    # --------------------------------------------------------

    if not is_failed:

        transaction_counter += 1

        continue

    # ========================================================
    # BANK DEGRADATION
    # ========================================================

    hour = (
        transaction_time.hour
    )

    bank_degradation = (

        hour in [
            19,
            20,
            21,
        ]

        and failure_reason in [
            "bank_timeout",
            "network_error",
        ]

        and random.random() < 0.45
    )

    # ========================================================
    # NUMBER OF PAYMENT ATTEMPTS
    # ========================================================

    attempt_number = random.choices(

        [
            1,
            2,
            3,
        ],

        weights=[
            0.70,
            0.23,
            0.07,
        ],

        k=1,
    )[0]

    # ========================================================
    # PAYMENT ATTEMPTS
    # ========================================================

    # First attempt happens shortly after the original
    # transaction time.
    current_attempt_time = (
        transaction_time
        + timedelta(
            minutes=random.randint(1, 15)
        )
    )

    for current_attempt in range(
        1,
        attempt_number + 1
    ):

        attempt_id = (
            f"ATT_{attempt_counter:07d}"
        )

        # Every subsequent attempt happens AFTER
        # the previous attempt.
        if current_attempt > 1:

            current_attempt_time = (
                current_attempt_time
                + timedelta(
                    minutes=random.randint(
                        5,
                        60
                    )
                )
            )

        attempt_time = current_attempt_time

        attempt_status = "failed"

        attempt_failure_reason = (
            failure_reason
        )

        response_code = (
            RESPONSE_CODES[
                attempt_failure_reason
            ]
        )

        processing_time_ms = (
            random.randint(
                150,
                5000
            )
        )

        payment_attempts.append({

            "attempt_id":
                attempt_id,

            "transaction_id":
                transaction_id,

            "attempt_number":
                current_attempt,

            "attempt_time":
                attempt_time,

            "payment_method":
                payment_method,

            "failure_reason":
                attempt_failure_reason,

            "response_code":
                response_code,

            "processing_time_ms":
                processing_time_ms,

            "status":
                attempt_status,
        })

        attempt_counter += 1

    # ========================================================
    # RECOVERY PROBABILITY
    # ========================================================

    recovery_probability = (
        calculate_recovery_probability(

            failure_reason=
                failure_reason,

            historical_success_rate=
                customer[
                    "historical_success_rate"
                ],

            attempt_number=
                attempt_number,

            payment_method=
                payment_method,

            bank_degradation=
                bank_degradation,
        )
    )

    # ========================================================
    # RECOVERY ACTION
    # ========================================================

    recovery_action = (
        choose_recovery_action(

            recovery_probability=
                recovery_probability,

            failure_reason=
                failure_reason,

            attempt_number=
                attempt_number,

            amount=
                amount,
        )
    )

    # ========================================================
    # RECOVERY OUTCOME
    # ========================================================

    recovered = (
        simulate_recovery(

            recovery_probability,
            recovery_action
        )
    )

    recovered_amount = (

        amount

        if recovered

        else 0
    )

    # ========================================================
    # INTERVENTION COST
    # ========================================================

    intervention_costs = {

        "retry_now":
            0.50,

        "retry_later":
            0.25,

        "send_reminder":
            0.10,

        "alternate_payment":
            0.30,

        "escalate":
            10.00,

        "stop":
            0.00,
    }

    intervention_cost = (
        intervention_costs[
            recovery_action
        ]
    )

    # ========================================================
    # RECOVERY TIME
    # ========================================================

    recovery_time_minutes = (

        random.randint(
            1,
            180
        )

        if recovered

        else None
    )

    recovery_outcomes.append({

        "transaction_id":
            transaction_id,

        "recovery_eligible":
            (
                recovery_probability
                >= 0.20
            ),

        "recovery_action":
            recovery_action,

        "recovery_probability":
            round(
                recovery_probability,
                4
            ),

        "recovered":
            recovered,

        "recovered_amount":
            round(
                recovered_amount,
                2
            ),

        "intervention_cost":
            intervention_cost,

        "recovery_time_minutes":
            recovery_time_minutes,
    })

    transaction_counter += 1


# ============================================================
# 3. CREATE DATAFRAMES
# ============================================================

transactions_df = pd.DataFrame(
    transactions
)

payment_attempts_df = pd.DataFrame(
    payment_attempts
)

recovery_outcomes_df = pd.DataFrame(
    recovery_outcomes
)


# ============================================================
# 4. SAVE DATA
# ============================================================

customers_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "customers.csv"
    ),
    index=False
)

transactions_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "transactions.csv"
    ),
    index=False
)

payment_attempts_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "payment_attempts.csv"
    ),
    index=False
)

recovery_outcomes_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "recovery_outcomes.csv"
    ),
    index=False
)


# ============================================================
# 5. BASIC VALIDATION
# ============================================================

print("\n======================================")
print("RecoverOS Synthetic Dataset Generated")
print("======================================")

print(
    f"\nCustomers: "
    f"{len(customers_df):,}"
)

print(
    f"Transactions: "
    f"{len(transactions_df):,}"
)

print(
    f"Payment attempts: "
    f"{len(payment_attempts_df):,}"
)

print(
    f"Recovery records: "
    f"{len(recovery_outcomes_df):,}"
)


# ============================================================
# CUSTOMER VALIDATION
# ============================================================

customer_count_consistency = (
    customers_df[
        "successful_transactions"
    ]
    +
    customers_df[
        "failed_transactions"
    ]
    ==
    customers_df[
        "total_transactions"
    ]
).all()


customer_rate_consistency = np.allclose(

    customers_df[
        "historical_success_rate"
    ],

    (
        customers_df[
            "successful_transactions"
        ]
        /
        customers_df[
            "total_transactions"
        ]
    ),

    atol=0.0001
)


print("\nCustomer validation:")

print(
    "Transaction counts consistent:",
    customer_count_consistency
)

print(
    "Historical success rates consistent:",
    customer_rate_consistency
)


# ============================================================
# TRANSACTION VALIDATION
# ============================================================

transaction_ids = set(
    transactions_df[
        "transaction_id"
    ]
)

customer_ids = set(
    customers_df[
        "customer_id"
    ]
)

transaction_customer_ids = set(
    transactions_df[
        "customer_id"
    ]
)

print("\nTransaction validation:")

print(
    "Unique transaction IDs:",
    transactions_df[
        "transaction_id"
    ].is_unique
)

print(
    "All transaction customers exist:",
    transaction_customer_ids.issubset(
        customer_ids
    )
)

print(
    "All amounts positive:",
    (
        transactions_df[
            "amount"
        ] > 0
    ).all()
)


# ============================================================
# PAYMENT ATTEMPT VALIDATION
# ============================================================

attempt_transaction_ids = set(
    payment_attempts_df[
        "transaction_id"
    ]
)

print("\nPayment attempt validation:")

print(
    "All attempt transactions exist:",
    attempt_transaction_ids.issubset(
        transaction_ids
    )
)

print(
    "Unique attempt IDs:",
    payment_attempts_df[
        "attempt_id"
    ].is_unique
)


# ============================================================
# RECOVERY VALIDATION
# ============================================================

failed_transaction_ids = set(
    transactions_df.loc[
        transactions_df[
            "status"
        ] == "failed",
        "transaction_id"
    ]
)

recovery_transaction_ids = set(
    recovery_outcomes_df[
        "transaction_id"
    ]
)

print("\nRecovery validation:")

print(
    "All failed transactions have recovery records:",
    failed_transaction_ids == recovery_transaction_ids
)

print(
    "Recovery probability within 0-1:",
    (
        recovery_outcomes_df[
            "recovery_probability"
        ].between(
            0,
            1
        )
    ).all()
)

print(
    "Recovered amount <= transaction amount:",
    (
        recovery_outcomes_df.merge(
            transactions_df[
                [
                    "transaction_id",
                    "amount",
                ]
            ],
            on="transaction_id",
            how="left"
        )[
            "recovered_amount"
        ]
        <=
        recovery_outcomes_df.merge(
            transactions_df[
                [
                    "transaction_id",
                    "amount",
                ]
            ],
            on="transaction_id",
            how="left"
        )[
            "amount"
        ]
    ).all()
)


# ============================================================
# DISTRIBUTION SUMMARY
# ============================================================

print("\nTransaction status:")
print(
    transactions_df[
        "status"
    ].value_counts()
)


print("\nFailure reasons:")
print(
    transactions_df.loc[
        transactions_df[
            "status"
        ] == "failed",
        "failure_reason"
    ].value_counts()
)


print("\nRecovery actions:")
print(
    recovery_outcomes_df[
        "recovery_action"
    ].value_counts()
)


print("\nRecovery outcomes:")
print(
    recovery_outcomes_df[
        "recovered"
    ].value_counts()
)


# ============================================================
# REVENUE SUMMARY
# ============================================================

failed_transactions_df = (
    transactions_df[
        transactions_df[
            "status"
        ] == "failed"
    ]
)

total_revenue_at_risk = (
    failed_transactions_df[
        "amount"
    ].sum()
)

total_recovered = (
    recovery_outcomes_df[
        "recovered_amount"
    ].sum()
)

recovery_rate = (

    total_recovered
    /
    total_revenue_at_risk

    if total_revenue_at_risk > 0

    else 0
)


print(
    f"\nTotal revenue at risk: "
    f"₹{total_revenue_at_risk:,.2f}"
)

print(
    f"Simulated recovered revenue: "
    f"₹{total_recovered:,.2f}"
)

print(
    f"Recovery rate by value: "
    f"{recovery_rate:.2%}"
)


print("\nFiles saved inside ./data/")

print("======================================")
print("Dataset generation completed.")
print("======================================\n")