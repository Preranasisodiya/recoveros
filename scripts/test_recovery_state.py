from src.agent.recovery_state import (
    RecoveryState
)


print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery State Test"
)

print(
    "=========================================="
)


# ============================================================
# CREATE STATE
# ============================================================

state = RecoveryState(

    transaction_id="TXN_STATE_001",

    amount=7499.00,

    failure_reason="bank_timeout",

    payment_method="card",

    attempt_number=1,
)


print(
    "\nInitial state:"
)

print(
    state.summary()
)


# ============================================================
# ADD ANALYSIS RESULTS
# ============================================================

state.risk_score = 0.6993

state.risk_level = "HIGH"

state.root_cause = (
    "Bank or issuer timeout"
)

state.cause_category = (
    "BANK_OR_NETWORK"
)

state.cause_nature = "temporary"

state.root_cause_confidence = 0.92

state.recovery_direction = "retry"

state.recovery_probability = 0.8414

state.decision = "retry_now"

state.decision_confidence = 0.90

state.decision_reason = (
    "High recovery probability and a "
    "temporary failure indicate an immediate "
    "retry is appropriate."
)


# ============================================================
# RECORD ACTION
# ============================================================

state.record_action(

    action="retry",

    result="success",

    amount_recovered=7499.00,

    details="Payment successfully recovered.",
)


# ============================================================
# MARK RECOVERED
# ============================================================

state.mark_recovered(
    7499.00
)


# ============================================================
# DISPLAY FINAL STATE
# ============================================================

print(
    "\nFinal state:"
)

print(
    state.summary()
)


print(
    "\nIs recovered:",
    state.is_recovered()
)

print(
    "Is terminal:",
    state.is_terminal()
)

print(
    "Recovered amount:",
    f"₹{state.recovered_amount:,.2f}"
)


print(
    "\n=========================================="
)

print(
    "Recovery State Test Completed"
)

print(
    "==========================================\n"
)