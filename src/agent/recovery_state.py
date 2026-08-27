from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class RecoveryState:
    """
    Represents the current state of a payment recovery case.

    The state is updated throughout the recovery lifecycle:

        payment failure
              ↓
        risk analysis
              ↓
        root cause analysis
              ↓
        recovery prediction
              ↓
        decision
              ↓
        action
              ↓
        outcome
    """

    # ========================================================
    # TRANSACTION INFORMATION
    # ========================================================

    transaction_id: str
    amount: float

    failure_reason: Optional[str] = None
    payment_method: Optional[str] = None

    attempt_number: int = 1

    # ========================================================
    # RISK INFORMATION
    # ========================================================

    risk_score: Optional[float] = None
    risk_level: Optional[str] = None

    # ========================================================
    # ROOT CAUSE INFORMATION
    # ========================================================

    root_cause: Optional[str] = None
    cause_category: Optional[str] = None
    cause_nature: Optional[str] = None
    root_cause_confidence: Optional[float] = None

    recovery_direction: Optional[str] = None

    # ========================================================
    # ML RECOVERY PREDICTION
    # ========================================================

    recovery_probability: Optional[float] = None

    # ========================================================
    # DECISION
    # ========================================================

    decision: Optional[str] = None
    decision_confidence: Optional[float] = None
    decision_reason: Optional[str] = None

    # ========================================================
    # RECOVERY ACTIONS
    # ========================================================

    actions_taken: List[Dict] = field(
        default_factory=list
    )

    # ========================================================
    # CURRENT RECOVERY STATUS
    # ========================================================

    status: str = "recovery_pending"

    # ========================================================
    # RECOVERY RESULT
    # ========================================================

    recovered_amount: float = 0.0

    # ========================================================
    # FAILURE / ESCALATION
    # ========================================================

    escalation_required: bool = False

    escalation_reason: Optional[str] = None

    # ========================================================
    # STATE UPDATE METHODS
    # ========================================================

    def record_action(
        self,
        action: str,
        result: str,
        amount_recovered: float = 0.0,
        details: Optional[str] = None,
    ):
        """
        Record an action taken by the recovery agent.
        """

        action_record = {
            "action": action,
            "result": result,
            "amount_recovered": amount_recovered,
            "details": details,
        }

        self.actions_taken.append(
            action_record
        )

        if amount_recovered > 0:

            self.recovered_amount += (
                amount_recovered
            )

    def mark_recovered(
        self,
        amount: Optional[float] = None,
    ):
        """
        Mark the transaction as successfully recovered.
        """

        self.status = "recovered"

        if amount is not None:

            self.recovered_amount = amount

        elif self.recovered_amount == 0:

            self.recovered_amount = self.amount

    def mark_failed(
        self,
        reason: Optional[str] = None,
    ):
        """
        Mark recovery as failed.
        """

        self.status = "recovery_failed"

        if reason:

            self.escalation_reason = reason

    def mark_escalated(
        self,
        reason: Optional[str] = None,
    ):
        """
        Mark the case as requiring manual intervention.
        """

        self.status = "escalated"

        self.escalation_required = True

        if reason:

            self.escalation_reason = reason

    def mark_stopped(
        self,
        reason: Optional[str] = None,
    ):
        """
        Stop automated recovery.
        """

        self.status = "stopped"

        if reason:

            self.escalation_reason = reason

    def is_recovered(self) -> bool:
        """
        Return True when revenue has been recovered.
        """

        return self.status == "recovered"

    def is_terminal(self) -> bool:
        """
        Return True when the recovery workflow
        should no longer continue automatically.
        """

        return self.status in {
            "recovered",
            "recovery_failed",
            "escalated",
            "stopped",
        }

    def summary(self) -> Dict:
        """
        Return a compact representation of the
        current recovery state.
        """

        return {
            "transaction_id":
                self.transaction_id,

            "amount":
                self.amount,

            "attempt_number":
                self.attempt_number,

            "risk_score":
                self.risk_score,

            "risk_level":
                self.risk_level,

            "root_cause":
                self.root_cause,

            "root_cause_confidence":
                self.root_cause_confidence,

            "recovery_probability":
                self.recovery_probability,

            "decision":
                self.decision,

            "decision_confidence":
                self.decision_confidence,

            "actions_taken":
                self.actions_taken,

            "status":
                self.status,

            "recovered_amount":
                self.recovered_amount,

            "escalation_required":
                self.escalation_required,

            "escalation_reason":
                self.escalation_reason,
        }