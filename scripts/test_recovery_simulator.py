from src.agent.recovery_state import RecoveryState
from src.recovery.recovery_simulator import (
    RecoverySimulator
)


print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery Action Simulator"
)

print(
    "=========================================="
)


simulator = RecoverySimulator()


# ============================================================
# TEST 1 — SUCCESSFUL RETRY
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Test 1: Successful retry"
)

print(
    "------------------------------------------"
)


state_1 = RecoveryState(

    transaction_id="TXN_SIM_001",

    amount=7499.00,

    failure_reason="bank_timeout",

    payment_method="card",

    attempt_number=1,
)

state_1.recovery_probability = 0.8345

state_1.decision = "retry_now"

state_1.decision_reason = (
    "High recovery probability and a temporary "
    "failure indicate an immediate retry is "
    "appropriate."
)


simulator.execute(
    state_1,
    forced_outcome="success",
)


print(
    f"Transaction: "
    f"{state_1.transaction_id}"
)

print(
    f"Amount: "
    f"₹{state_1.amount:,.2f}"
)

print(
    f"Decision: "
    f"{state_1.decision}"
)

print(
    f"Status: "
    f"{state_1.status}"
)

print(
    f"Recovered amount: "
    f"₹{state_1.recovered_amount:,.2f}"
)


# ============================================================
# TEST 2 — FAILED RETRY
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Test 2: Failed retry"
)

print(
    "------------------------------------------"
)


state_2 = RecoveryState(

    transaction_id="TXN_SIM_002",

    amount=5000.00,

    failure_reason="network_error",

    payment_method="card",

    attempt_number=1,
)

state_2.recovery_probability = 0.65

state_2.decision = "retry_now"

state_2.decision_reason = (
    "Recovery remains plausible."
)


simulator.execute(
    state_2,
    forced_outcome="failure",
)


print(
    f"Transaction: "
    f"{state_2.transaction_id}"
)

print(
    f"Amount: "
    f"₹{state_2.amount:,.2f}"
)

print(
    f"Decision: "
    f"{state_2.decision}"
)

print(
    f"Status: "
    f"{state_2.status}"
)

print(
    f"Recovered amount: "
    f"₹{state_2.recovered_amount:,.2f}"
)


# ============================================================
# TEST 3 — ALTERNATE PAYMENT SUCCESS
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Test 3: Alternate payment"
)

print(
    "------------------------------------------"
)


state_3 = RecoveryState(

    transaction_id="TXN_SIM_003",

    amount=5000.00,

    failure_reason="expired_card",

    payment_method="card",

    attempt_number=1,
)

state_3.recovery_probability = 0.72

state_3.decision = "alternate_payment"

state_3.decision_reason = (
    "Alternate payment method is preferred."
)


simulator.execute(
    state_3,
    forced_outcome="success",
)


print(
    f"Transaction: "
    f"{state_3.transaction_id}"
)

print(
    f"Decision: "
    f"{state_3.decision}"
)

print(
    f"Status: "
    f"{state_3.status}"
)

print(
    f"Recovered amount: "
    f"₹{state_3.recovered_amount:,.2f}"
)


# ============================================================
# TEST 4 — ESCALATION
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Test 4: High-value escalation"
)

print(
    "------------------------------------------"
)


state_4 = RecoveryState(

    transaction_id="TXN_SIM_004",

    amount=75000.00,

    failure_reason="bank_timeout",

    payment_method="card",

    attempt_number=1,
)

state_4.recovery_probability = 0.7591

state_4.decision = "escalate"

state_4.decision_reason = (
    "High-value transaction requires additional "
    "control before automated recovery."
)


simulator.execute(
    state_4
)


print(
    f"Transaction: "
    f"{state_4.transaction_id}"
)

print(
    f"Amount: "
    f"₹{state_4.amount:,.2f}"
)

print(
    f"Decision: "
    f"{state_4.decision}"
)

print(
    f"Status: "
    f"{state_4.status}"
)

print(
    f"Escalation required: "
    f"{state_4.escalation_required}"
)

print(
    f"Recovered amount: "
    f"₹{state_4.recovered_amount:,.2f}"
)


# ============================================================
# TEST 5 — STOP
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "Test 5: Stop recovery"
)

print(
    "------------------------------------------"
)


state_5 = RecoveryState(

    transaction_id="TXN_SIM_005",

    amount=2500.00,

    failure_reason="expired_card",

    payment_method="card",

    attempt_number=1,
)

state_5.recovery_probability = 0.25

state_5.decision = "stop"

state_5.decision_reason = (
    "Recovery probability is too low."
)


simulator.execute(
    state_5
)


print(
    f"Transaction: "
    f"{state_5.transaction_id}"
)

print(
    f"Decision: "
    f"{state_5.decision}"
)

print(
    f"Status: "
    f"{state_5.status}"
)

print(
    f"Recovered amount: "
    f"₹{state_5.recovered_amount:,.2f}"
)


print(
    "\n=========================================="
)

print(
    "Recovery Simulator Test Completed"
)

print(
    "==========================================\n"
)