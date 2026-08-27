from src.risk.revenue_risk_detector import (
    RevenueRiskDetector
)


detector = RevenueRiskDetector()


transaction = {

    "transaction_id":
        "TXN_TEST_001",

    "amount":
        7499,

    "status":
        "failed",

    "failure_reason":
        "bank_timeout",

    "payment_method":
        "UPI",

    "attempt_number":
        1,

    "historical_success_rate":
        0.91,

    "checkout_completed":
        True,
}


result = detector.detect(
    transaction
)


print("\n========== RISK RESULT ==========")

print(
    "Transaction:",
    result["transaction_id"]
)

print(
    "Revenue at risk:",
    f"₹{result['revenue_at_risk']:,.2f}"
)

print(
    "Risk score:",
    result["risk_score"]
)

print(
    "Risk level:",
    result["risk_level"]
)

print(
    "Recovery eligible:",
    result["recovery_eligible"]
)

print("\nWhy?")

for reason in result["explanation"]:

    print(
        "•",
        reason
    )