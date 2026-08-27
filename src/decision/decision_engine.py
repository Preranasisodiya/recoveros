class DecisionEngine:
    """
    Bounded recovery decision engine.

    Combines:
        - Revenue risk
        - Root cause
        - ML recovery probability
        - Attempt history
        - Transaction value

    Produces:
        - Recovery action
        - Decision confidence
        - Reason
    """

    def decide(
        self,
        risk_score,
        risk_level,
        recovery_probability,
        root_cause,
        recovery_direction,
        attempt_number,
        amount,
    ):

        # ====================================================
        # SAFETY CONTROL 1
        # HIGH-VALUE TRANSACTIONS
        # ====================================================

        if amount > 50000:

            return {
                "action": "escalate",

                "decision_confidence": 0.98,

                "reason":
                    "High-value transaction requires "
                    "additional control before automated recovery.",
            }

        # ====================================================
        # SAFETY CONTROL 2
        # MAXIMUM RETRY ATTEMPTS
        # ====================================================

        if attempt_number >= 3:

            if recovery_direction == "alternate_payment":

                return {
                    "action": "alternate_payment",

                    "decision_confidence": 0.95,

                    "reason":
                        "Maximum retry threshold reached; "
                        "another payment method is preferred.",
                }

            return {
                "action": "stop",

                "decision_confidence": 0.96,

                "reason":
                    "Maximum automated retry threshold "
                    "has been reached.",
            }

        # ====================================================
        # PAYMENT INSTRUMENT PROBLEMS
        # ====================================================

        if recovery_direction == "alternate_payment":

            if recovery_probability >= 0.40:

                return {
                    "action": "alternate_payment",

                    "decision_confidence": 0.92,

                    "reason":
                        "Root cause indicates that retrying "
                        "the current payment instrument is unlikely "
                        "to address the underlying issue.",
                }

            return {
                "action": "stop",

                "decision_confidence": 0.88,

                "reason":
                    "Low recovery probability combined with "
                    "a payment-instrument issue.",
            }

        # ====================================================
        # CUSTOMER ACTION REQUIRED
        # ====================================================

        if recovery_direction == "customer_action":

            if recovery_probability >= 0.50:

                return {
                    "action": "send_reminder",

                    "decision_confidence": 0.86,

                    "reason":
                        "Customer action is required before "
                        "another payment attempt.",
                }

            return {
                "action": "stop",

                "decision_confidence": 0.84,

                "reason":
                    "Low recovery probability and customer "
                    "action is required.",
            }

        # ====================================================
        # ESCALATION
        # ====================================================

        if recovery_direction == "escalate":

            return {
                "action": "escalate",

                "decision_confidence": 0.90,

                "reason":
                    "Payment context requires controlled "
                    "manual intervention.",
            }

        # ====================================================
        # TEMPORARY FAILURE / RETRY LOGIC
        # ====================================================

        if recovery_direction == "retry":

            # Very strong recovery opportunity.
            if recovery_probability >= 0.75:

                return {
                    "action": "retry_now",

                    "decision_confidence": 0.90,

                    "reason":
                        "High recovery probability and a "
                        "temporary failure indicate an immediate "
                        "retry is appropriate.",
                }

            # Reasonable recovery opportunity.
            if recovery_probability >= 0.50:

                return {
                    "action": "retry_later",

                    "decision_confidence": 0.82,

                    "reason":
                        "Recovery remains plausible, but delaying "
                        "the retry reduces unnecessary immediate "
                        "retries.",
                }

            # Moderate-low recovery opportunity.
            if recovery_probability >= 0.30:

                return {
                    "action": "send_reminder",

                    "decision_confidence": 0.76,

                    "reason":
                        "Recovery probability is moderate-low; "
                        "customer engagement is preferred over "
                        "another immediate retry.",
                }

            return {
                "action": "stop",

                "decision_confidence": 0.85,

                "reason":
                    "Recovery probability is too low to justify "
                    "another automated attempt.",
            }

        # ====================================================
        # DEFAULT SAFETY FALLBACK
        # ====================================================

        return {
            "action": "escalate",

            "decision_confidence": 0.70,

            "reason":
                "No safe automated recovery strategy "
                "could be established.",
        }