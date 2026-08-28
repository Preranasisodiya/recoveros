import os

import pandas as pd

from src.risk.revenue_risk_detector import RevenueRiskDetector
from src.root_cause.root_cause_engine import RootCauseEngine
from src.ml.recovery_model import RecoveryProbabilityModel
from src.decision.decision_engine import DecisionEngine
from src.recovery.recovery_simulator import RecoverySimulator

from src.agent.recovery_state import RecoveryState


class RecoveryAgent:
    """
    RecoverOS end-to-end recovery orchestrator.

    The agent coordinates:

        1. Revenue Risk Detector
        2. Root Cause Engine
        3. Recovery Probability Model
        4. Decision Engine
        5. Recovery State

    The agent does not duplicate the business logic of
    these components. It orchestrates them and maintains
    the state of the recovery workflow.
    """

    def __init__(
        self,
        model_path="models/recovery_probability_model.joblib",
    ):
        """
        Initialize all RecoverOS components.
        """

        self.risk_detector = RevenueRiskDetector()

        self.root_cause_engine = RootCauseEngine()

        self.recovery_model = RecoveryProbabilityModel()

        self.decision_engine = DecisionEngine()

        self.recovery_simulator = RecoverySimulator()

        self.model_path = model_path

        self._load_model()

    # ========================================================
    # MODEL LOADING
    # ========================================================

    def _load_model(self):
        """
        Load the trained recovery probability model.
        """

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Recovery model not found: {self.model_path}"
            )

        self.recovery_model.load(
            self.model_path
        )

    # ========================================================
    # MODEL INPUT
    # ========================================================

    def _prepare_model_input(self, transaction):
        """
        Prepare one transaction for the trained
        recovery probability model.

        The feature names exactly match the features
        used during model training.
        """

        required_features = [
            "amount",
            "attempt_number",
            "historical_success_rate",
            "customer_tenure_days",
            "avg_transaction_amount",
            "transaction_hour",
            "payment_method",
            "bank",
            "failure_reason",
            "checkout_completed",
            "subscription_flag",
        ]

        data = {}

        for feature in required_features:

            if feature not in transaction:
                raise ValueError(
                    f"Required model feature missing: {feature}"
                )

            data[feature] = transaction[feature]

        return pd.DataFrame(
            [data],
            columns=required_features,
        )

    # ========================================================
    # ACTION MAPPING
    # ========================================================

    def _map_action_to_status(self, action):
        """
        Convert a decision-engine action into the
        corresponding recovery workflow status.
        """

        if action == "escalate":
            return "escalated"

        if action == "stop":
            return "stopped"

        return "recovery_pending"

    # ========================================================
    # MAIN AGENT WORKFLOW
    # ========================================================

    def process(self, transaction):
        """
        Process one failed payment through the complete
        RecoverOS decision pipeline.

        Returns:
            RecoveryState
        """

        # ----------------------------------------------------
        # Validate transaction
        # ----------------------------------------------------

        if not isinstance(transaction, dict):
            raise TypeError(
                "Transaction must be provided as a dictionary."
            )

        transaction_id = transaction.get(
            "transaction_id"
        )

        amount = float(
            transaction.get(
                "amount",
                0,
            )
        )

        attempt_number = int(
            transaction.get(
                "attempt_number",
                1,
            )
        )

        failure_reason = transaction.get(
            "failure_reason"
        )

        payment_method = transaction.get(
            "payment_method"
        )

        # ----------------------------------------------------
        # Create recovery state
        # ----------------------------------------------------

        state = RecoveryState(

            transaction_id=transaction_id,

            amount=amount,

            failure_reason=failure_reason,

            payment_method=payment_method,

            attempt_number=attempt_number,
        )

        # ====================================================
        # STEP 1 — RISK DETECTION
        # ====================================================

        risk_result = self.risk_detector.detect(
            transaction
        )

        state.risk_score = risk_result.get(
            "risk_score"
        )

        state.risk_level = risk_result.get(
            "risk_level"
        )

        # ----------------------------------------------------
        # Record risk assessment in audit trail
        # ----------------------------------------------------

        state.record_action(

            action="risk_assessment",

            result="completed",

            details=(
                f"Risk score "
                f"{state.risk_score:.4f}; "
                f"level {state.risk_level}."
            ),
        )

        # ====================================================
        # STEP 2 — ROOT CAUSE ANALYSIS
        # ====================================================

        root_cause_result = (
            self.root_cause_engine.analyze(
                transaction
            )
        )

        state.root_cause = (
            root_cause_result.get(
                "root_cause"
            )
        )

        state.cause_category = (
            root_cause_result.get(
                "cause_category"
            )
        )

        state.cause_nature = (
            root_cause_result.get(
                "nature"
            )
        )

        state.root_cause_confidence = (
            root_cause_result.get(
                "confidence"
            )
        )

        state.recovery_direction = (
            root_cause_result.get(
                "recommended_direction"
            )
        )

        state.record_action(

            action="root_cause_analysis",

            result="completed",

            details=(
                f"{state.root_cause}; "
                f"direction "
                f"{state.recovery_direction}."
            ),
        )

        # ====================================================
        # STEP 3 — RECOVERY PROBABILITY
        # ====================================================

        model_input = (
            self._prepare_model_input(
                transaction
            )
        )

        probability = (
            self.recovery_model.predict_probability(
                model_input
            )[0]
        )

        state.recovery_probability = round(
            float(probability),
            4,
        )

        state.record_action(

            action="recovery_prediction",

            result="completed",

            details=(
                f"Recovery probability "
                f"{state.recovery_probability:.2%}."
            ),
        )
        # ====================================================
        # STEP 4 — DECISION ENGINE
        # ====================================================

        decision_result = (
            self.decision_engine.decide(

                risk_score=state.risk_score,

                risk_level=state.risk_level,

                recovery_probability=(
                    state.recovery_probability
                ),

                root_cause=state.root_cause,

                recovery_direction=(
                    state.recovery_direction
                ),

                attempt_number=(
                    state.attempt_number
                ),

                amount=state.amount,
            )
        )

        # ----------------------------------------------------
        # Store decision result in recovery state
        # ----------------------------------------------------

        state.decision = decision_result.get(
            "action"
        )

        state.decision_confidence = (
            decision_result.get(
                "decision_confidence"
            )
        )

        state.decision_reason = (
            decision_result.get(
                "reason"
            )
        )

        state.record_action(

            action="decision",

            result="completed",

            details=(
                f"Decision: {state.decision}; "
                f"confidence: "
                f"{state.decision_confidence:.2f}."
            ),
        )

        # ====================================================
        # STEP 5 — DECISION SAFETY BOUNDARY
        # ====================================================

        action = state.decision

        # ----------------------------------------------------
        # Escalation
        # ----------------------------------------------------

        if action == "escalate":

            state.mark_escalated(
                state.decision_reason
            )

            state.record_action(

                action="escalate",

                result="manual_intervention_required",

                details=state.decision_reason,
            )

            return state

        # ----------------------------------------------------
        # Stop
        # ----------------------------------------------------

        if action == "stop":

            state.mark_stopped(
                state.decision_reason
            )

            state.record_action(

                action="stop",

                result="automated_recovery_stopped",

                details=state.decision_reason,
            )

            return state

        # ----------------------------------------------------
        # Automated recovery action
        # ----------------------------------------------------

        state.status = (
            self._map_action_to_status(
                action
            )
        )

        state.record_action(

            action=action,

            result="action_selected",

            details=state.decision_reason,
        )

        return state

    def execute_recovery(
        self,
        state,
        forced_outcome=None,
    ):
        """
        Execute the recovery action selected by the
        Decision Engine.

        The RecoverySimulator performs only safe,
        simulated actions.

        Returns:
            Updated RecoveryState
        """

        if not isinstance(
            state,
            RecoveryState,
        ):
            raise TypeError(
                "state must be a RecoveryState instance."
            )

        return self.recovery_simulator.execute(
            state,
            forced_outcome=forced_outcome,
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def process_and_summarize(
        self,
        transaction,
    ):
        """
        Process a transaction and return a compact
        dictionary representation of the state.
        """

        state = self.process(
            transaction
        )

        return state.summary()