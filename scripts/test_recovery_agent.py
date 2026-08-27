from src.agent.recovery_agent import RecoveryAgent


print(
    "\n=========================================="
)

print(
    "RecoverOS Recovery Agent Test"
)

print(
    "=========================================="
)


# ============================================================
# TEST TRANSACTION
# ============================================================

transaction = {

    "transaction_id":
        "TXN_AGENT_001",

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
}


# ============================================================
# INITIALIZE AGENT
# ============================================================

agent = RecoveryAgent()


# ============================================================
# PROCESS TRANSACTION
# ============================================================

state = agent.process(
    transaction
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print(
    "\nTransaction:"
)

print(
    state.transaction_id
)

print(
    "\nAmount:"
)

print(
    f"₹{state.amount:,.2f}"
)

print(
    "\nRisk:"
)

print(
    f"Score: {state.risk_score:.4f}"
)

print(
    f"Level: {state.risk_level}"
)

print(
    "\nRoot Cause:"
)

print(
    state.root_cause
)

print(
    f"Nature: {state.cause_nature}"
)

print(
    f"Confidence: "
    f"{state.root_cause_confidence:.2%}"
)

print(
    "\nRecovery Probability:"
)

print(
    f"{state.recovery_probability:.2%}"
)

print(
    "\nDecision:"
)

print(
    state.decision
)

print(
    f"Confidence: "
    f"{state.decision_confidence:.2%}"
)

print(
    "\nReason:"
)

print(
    state.decision_reason
)

print(
    "\nStatus:"
)

print(
    state.status
)

print(
    "\nAudit Trail:"
)

for index, action in enumerate(
    state.actions_taken,
    start=1,
):

    print(
        f"{index}. "
        f"{action['action']} → "
        f"{action['result']}"
    )

print(
    "\n=========================================="
)

print(
    "Recovery Agent Test Completed"
)

print(
    "==========================================\n"
)

# ============================================================
# HIGH-VALUE SAFETY TEST
# ============================================================

print(
    "\n=========================================="
)

print(
    "High-Value Safety Test"
)

print(
    "=========================================="
)


high_value_transaction = {

    "transaction_id":
        "TXN_AGENT_HIGH_VALUE",

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
}


high_value_state = agent.process(
    high_value_transaction
)


print(
    "\nTransaction:"
)

print(
    high_value_state.transaction_id
)

print(
    "Amount:"
)

print(
    f"₹{high_value_state.amount:,.2f}"
)

print(
    "\nRecovery Probability:"
)

print(
    f"{high_value_state.recovery_probability:.2%}"
)

print(
    "\nDecision:"
)

print(
    high_value_state.decision
)

print(
    "\nStatus:"
)

print(
    high_value_state.status
)

print(
    "\nEscalation Required:"
)

print(
    high_value_state.escalation_required
)

print(
    "\nEscalation Reason:"
)

print(
    high_value_state.escalation_reason
)

print(
    "\n=========================================="
)