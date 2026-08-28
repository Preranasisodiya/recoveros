from src.agent.recovery_state import RecoveryState


class RecoverySimulator:
    """
    Safe, deterministic simulator for recovery actions.

    This component does NOT call a real payment gateway
    and does NOT move real money.

    It simulates the operational result of the decision
    produced by the RecoverOS Decision Engine.
    """

    def execute(
        self,
        state: RecoveryState,
        forced_outcome=None,
    ):
        """
        Execute the recovery action represented by
        the current RecoveryState.

        Parameters
        ----------
        state:
            Current RecoverOS recovery state.

        forced_outcome:
            Optional deterministic test outcome.

            Supported values:
                "success"
                "failure"

            If omitted, the simulator derives the outcome
            from the recovery probability.

        Returns
        -------
        RecoveryState
            Updated recovery state.
        """

        if not isinstance(state, RecoveryState):
            raise TypeError(
                "state must be a RecoveryState instance."
            )

        # ====================================================
        # TERMINAL STATE PROTECTION
        # ====================================================

        if state.is_terminal():

            return state

        # ====================================================
        # VALIDATE DECISION
        # ====================================================

        action = state.decision

        if action is None:

            raise ValueError(
                "Recovery decision is missing."
            )

        # ====================================================
        # ESCALATION
        # ====================================================

        if action == "escalate":

            state.mark_escalated(
                state.decision_reason
            )

            state.record_action(

                action="escalate",

                result="manual_intervention_required",

                details=(
                    "Automated recovery was blocked "
                    "and the transaction requires "
                    "manual review."
                ),
            )

            return state

        # ====================================================
        # STOP
        # ====================================================

        if action == "stop":

            state.mark_stopped(
                state.decision_reason
            )

            state.record_action(

                action="stop",

                result="automated_recovery_stopped",

                details=(
                    "No further automated recovery "
                    "action was executed."
                ),
            )

            return state

        # ====================================================
        # SEND REMINDER
        # ====================================================

        if action == "send_reminder":

            state.record_action(

                action="send_reminder",

                result="reminder_sent",

                details=(
                    "Customer reminder simulated "
                    "successfully."
                ),
            )

            state.status = "awaiting_customer_action"

            return state

        # ====================================================
        # RETRY LATER
        # ====================================================

        if action == "retry_later":

            state.record_action(

                action="retry_later",

                result="retry_scheduled",

                details=(
                    "Recovery retry scheduled for "
                    "a later attempt."
                ),
            )

            state.status = "retry_scheduled"

            return state

        # ====================================================
        # ALTERNATE PAYMENT
        # ====================================================

        if action == "alternate_payment":

            outcome = self._resolve_outcome(

                state,

                forced_outcome,
            )

            if outcome == "success":

                state.record_action(

                    action="alternate_payment",

                    result="success",

                    amount_recovered=state.amount,

                    details=(
                        "Alternate payment method "
                        "successfully recovered "
                        "the transaction."
                    ),
                )

                state.mark_recovered(
                    state.amount
                )

            else:

                state.record_action(

                    action="alternate_payment",

                    result="failure",

                    details=(
                        "Alternate payment attempt "
                        "did not recover the transaction."
                    ),
                )

                state.mark_failed(
                    "Alternate payment attempt failed."
                )

            return state

        # ====================================================
        # IMMEDIATE RETRY
        # ====================================================

        if action == "retry_now":

            outcome = self._resolve_outcome(

                state,

                forced_outcome,
            )

            if outcome == "success":

                state.record_action(

                    action="retry_now",

                    result="success",

                    amount_recovered=state.amount,

                    details=(
                        "Immediate retry successfully "
                        "recovered the transaction."
                    ),
                )

                state.mark_recovered(
                    state.amount
                )

            else:

                state.record_action(

                    action="retry_now",

                    result="failure",

                    details=(
                        "Immediate retry did not "
                        "recover the transaction."
                    ),
                )

                state.mark_failed(
                    "Immediate retry failed."
                )

            return state

        # ====================================================
        # UNKNOWN ACTION
        # ====================================================

        raise ValueError(
            f"Unsupported recovery action: {action}"
        )

    # ========================================================
    # OUTCOME RESOLUTION
    # ========================================================

    def _resolve_outcome(
        self,
        state: RecoveryState,
        forced_outcome=None,
    ):
        """
        Determine whether a simulated recovery action
        succeeds or fails.

        Forced outcomes are used for deterministic
        Buildathon demonstrations and testing.

        Otherwise, recovery probability determines
        the simulated outcome.
        """

        if forced_outcome is not None:

            if forced_outcome not in {
                "success",
                "failure",
            }:

                raise ValueError(
                    "forced_outcome must be "
                    "'success' or 'failure'."
                )

            return forced_outcome

        probability = (
            state.recovery_probability
        )

        if probability is None:

            raise ValueError(
                "Recovery probability is required "
                "to simulate an outcome."
            )

        # ----------------------------------------------------
        # Deterministic probability policy
        # ----------------------------------------------------

        if probability >= 0.75:

            return "success"

        if probability >= 0.50:

            return "success"

        return "failure"