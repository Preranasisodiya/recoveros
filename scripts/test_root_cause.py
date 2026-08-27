from src.root_cause.root_cause_engine import (
    RootCauseEngine
)


engine = RootCauseEngine()


test_transactions = [

    {
        "transaction_id": "TEST_TIMEOUT",
        "amount": 7499,
        "failure_reason": "bank_timeout",
        "attempt_number": 1,
    },

    {
        "transaction_id": "TEST_CARD",
        "amount": 4500,
        "failure_reason": "expired_card",
        "attempt_number": 1,
    },

    {
        "transaction_id": "TEST_FUNDS",
        "amount": 2500,
        "failure_reason": "insufficient_funds",
        "attempt_number": 2,
    },

    {
        "transaction_id": "TEST_REPEAT",
        "amount": 6000,
        "failure_reason": "bank_declined",
        "attempt_number": 3,
    },

    {
        "transaction_id": "TEST_HIGH_VALUE",
        "amount": 75000,
        "failure_reason": "bank_timeout",
        "attempt_number": 1,
    },
]


for transaction in test_transactions:

    result = engine.analyze(
        transaction
    )

    print("\n===================================")

    print(
        "Transaction:",
        result["transaction_id"]
    )

    print(
        "Root cause:",
        result["root_cause"]
    )

    print(
        "Category:",
        result["cause_category"]
    )

    print(
        "Nature:",
        result["nature"]
    )

    print(
        "Confidence:",
        result["confidence"]
    )

    print(
        "Recovery direction:",
        result["recommended_direction"]
    )

    print("\nWhy?")

    for reason in result["explanation"]:

        print(
            "•",
            reason
        )