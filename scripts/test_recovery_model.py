import pandas as pd

from src.ml.recovery_model import (
    RecoveryProbabilityModel
)


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_FILE = (
    "models/recovery_probability_model.joblib"
)

model = RecoveryProbabilityModel()

model.load(
    MODEL_FILE
)


# ============================================================
# CREATE A NEW FAILED PAYMENT
# ============================================================

transaction = pd.DataFrame([
    {
        "amount": 7499.00,

        "attempt_number": 1,

        "historical_success_rate": 0.91,

        "customer_tenure_days": 720,

        "avg_transaction_amount": 5200.00,

        "transaction_hour": 20,

        "payment_method": "UPI",

        "bank": "HDFC",

        "failure_reason": "bank_timeout",

        "checkout_completed": True,

        "subscription_flag": True,
    }
])


# ============================================================
# PREDICT
# ============================================================

probability = (
    model.predict_probability(
        transaction
    )[0]
)


prediction = (
    model.predict(
        transaction
    )[0]
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n==========================================")
print("RecoverOS Recovery Probability Inference")
print("==========================================")

print(
    f"\nRecovery probability: "
    f"{probability:.2%}"
)

print(
    "Predicted outcome:",
    "RECOVERABLE"
    if prediction == 1
    else "NOT RECOVERABLE"
)

print(
    "\n=========================================="
)