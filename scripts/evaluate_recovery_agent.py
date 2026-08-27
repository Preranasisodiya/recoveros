from src.agent.recovery_agent import RecoveryAgent


print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery Agent Evaluation"
)

print(
    "=========================================="
)


agent = RecoveryAgent()


# ============================================================
# TEST CASES
# ============================================================

test_cases = [

    {
        "name":
            "Temporary high-probability failure",

        "transaction": {

            "transaction_id":
                "AGENT_EVAL_001",

            "amount":
                7499.00,

            "status":
                "failed",

            "failure_reason":
                "bank_timeout",

            "payment_method":
                "card",

            "attempt_number":
                1,

            "historical_success_rate":
                0.91,

            "customer_tenure_days":
                420,

            "avg_transaction_amount":
                6500.00,

            "transaction_hour":
                14,

            "bank":
                "HDFC",

            "checkout_completed":
                True,

            "subscription_flag":
                False,
        },
    },

    {
        "name":
            "Expired card",

        "transaction": {

            "transaction_id":
                "AGENT_EVAL_002",

            "amount":
                5000.00,

            "status":
                "failed",

            "failure_reason":
                "expired_card",

            "payment_method":
                "card",

            "attempt_number":
                1,

            "historical_success_rate":
                0.90,

            "customer_tenure_days":
                500,

            "avg_transaction_amount":
                6000.00,

            "transaction_hour":
                12,

            "bank":
                "HDFC",

            "checkout_completed":
                True,

            "subscription_flag":
                False,
        },
    },

    {
        "name":
            "Low probability retry",

        "transaction": {

            "transaction_id":
                "AGENT_EVAL_003",

            "amount":
                2500.00,

            "status":
                "failed",

            "failure_reason":
                "insufficient_funds",

            "payment_method":
                "card",

            "attempt_number":
                3,

            "historical_success_rate":
                0.30,

            "customer_tenure_days":
                100,

            "avg_transaction_amount":
                4000.00,

            "transaction_hour":
                20,

            "bank":
                "SBI",

            "checkout_completed":
                True,

            "subscription_flag":
                False,
        },
    },

    {
        "name":
            "High-value transaction",

        "transaction": {

            "transaction_id":
                "AGENT_EVAL_004",

            "amount":
                75000.00,

            "status":
                "failed",

            "failure_reason":
                "bank_timeout",

            "payment_method":
                "card",

            "attempt_number":
                1,

            "historical_success_rate":
                0.95,

            "customer_tenure_days":
                800,

            "avg_transaction_amount":
                12000.00,

            "transaction_hour":
                14,

            "bank":
                "HDFC",

            "checkout_completed":
                True,

            "subscription_flag":
                False,
        },
    },

    {
        "name":
            "Maximum attempts",

        "transaction": {

            "transaction_id":
                "AGENT_EVAL_005",

            "amount":
                6000.00,

            "status":
                "failed",

            "failure_reason":
                "bank_declined",

            "payment_method":
                "card",

            "attempt_number":
                3,

            "historical_success_rate":
                0.80,

            "customer_tenure_days":
                600,

            "avg_transaction_amount":
                5000.00,

            "transaction_hour":
                16,

            "bank":
                "ICICI",

            "checkout_completed":
                True,

            "subscription_flag":
                False,
        },
    },
]


# ============================================================
# RUN EVALUATION
# ============================================================

for index, test_case in enumerate(
    test_cases,
    start=1,
):

    print(
        "\n------------------------------------------"
    )

    print(
        f"Test {index}: "
        f"{test_case['name']}"
    )

    print(
        "------------------------------------------"
    )

    state = agent.process(
        test_case["transaction"]
    )

    print(
        f"Transaction: "
        f"{state.transaction_id}"
    )

    print(
        f"Amount: "
        f"₹{state.amount:,.2f}"
    )

    print(
        f"Risk: "
        f"{state.risk_score:.4f} "
        f"({state.risk_level})"
    )

    print(
        f"Root cause: "
        f"{state.root_cause}"
    )

    print(
        f"Recovery probability: "
        f"{state.recovery_probability:.2%}"
    )

    print(
        f"Decision: "
        f"{state.decision}"
    )

    print(
        f"Status: "
        f"{state.status}"
    )

    print(
        f"Escalation required: "
        f"{state.escalation_required}"
    )

    print(
        "Audit events: "
        f"{len(state.actions_taken)}"
    )


print(
    "\n=========================================="
)

print(
    "Recovery Agent Evaluation Completed"
)

print(
    "==========================================\n"
)