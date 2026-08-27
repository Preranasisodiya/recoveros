from src.decision.decision_engine import (
    DecisionEngine
)


engine = DecisionEngine()


test_cases = [

    # ========================================================
    # CASE 1
    # Temporary failure + high probability
    # Expected: retry_now
    # ========================================================

    {
        "name":
            "Temporary high-probability failure",

        "risk_score":
            0.72,

        "risk_level":
            "CRITICAL",

        "recovery_probability":
            0.8414,

        "root_cause":
            "Bank or issuer timeout",

        "recovery_direction":
            "retry",

        "attempt_number":
            1,

        "amount":
            7499,
    },

    # ========================================================
    # CASE 2
    # Expired card
    # Expected: alternate_payment
    # ========================================================

    {
        "name":
            "Expired card",

        "risk_score":
            0.55,

        "risk_level":
            "MEDIUM",

        "recovery_probability":
            0.72,

        "root_cause":
            "Payment card has expired",

        "recovery_direction":
            "alternate_payment",

        "attempt_number":
            1,

        "amount":
            4500,
    },

    # ========================================================
    # CASE 3
    # Low probability retry
    # Expected: stop
    # ========================================================

    {
        "name":
            "Low probability retry",

        "risk_score":
            0.40,

        "risk_level":
            "MEDIUM",

        "recovery_probability":
            0.25,

        "root_cause":
            "Bank or issuer timeout",

        "recovery_direction":
            "retry",

        "attempt_number":
            1,

        "amount":
            2500,
    },

    # ========================================================
    # CASE 4
    # High-value transaction
    # Expected: escalate
    # ========================================================

    {
        "name":
            "High value transaction",

        "risk_score":
            0.72,

        "risk_level":
            "CRITICAL",

        "recovery_probability":
            0.88,

        "root_cause":
            "Bank or issuer timeout",

        "recovery_direction":
            "retry",

        "attempt_number":
            1,

        "amount":
            75000,
    },

    # ========================================================
    # CASE 5
    # Maximum attempts
    # Expected: stop
    # ========================================================

    {
        "name":
            "Maximum attempts",

        "risk_score":
            0.65,

        "risk_level":
            "HIGH",

        "recovery_probability":
            0.70,

        "root_cause":
            "Bank or issuer timeout",

        "recovery_direction":
            "retry",

        "attempt_number":
            3,

        "amount":
            5000,
    },
]


# ============================================================
# RUN TESTS
# ============================================================

for case in test_cases:

    result = engine.decide(

        risk_score=
            case["risk_score"],

        risk_level=
            case["risk_level"],

        recovery_probability=
            case["recovery_probability"],

        root_cause=
            case["root_cause"],

        recovery_direction=
            case["recovery_direction"],

        attempt_number=
            case["attempt_number"],

        amount=
            case["amount"],
    )

    print(
        "\n=========================================="
    )

    print(
        "Test:",
        case["name"]
    )

    print(
        "Recovery probability:",
        f"{case['recovery_probability']:.2%}"
    )

    print(
        "Action:",
        result["action"]
    )

    print(
        "Decision confidence:",
        result["decision_confidence"]
    )

    print(
        "Reason:",
        result["reason"]
    )