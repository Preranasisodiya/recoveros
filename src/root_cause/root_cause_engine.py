class RootCauseEngine:
    """
    Explainable root-cause engine for failed payments.

    Determines:
        1. Root cause
        2. Cause category
        3. Temporary vs persistent nature
        4. Confidence
        5. Recommended recovery direction
        6. Explanation
    """

    FAILURE_RULES = {

        "bank_timeout": {
            "root_cause": "Bank or issuer timeout",
            "cause_category": "BANK_OR_NETWORK",
            "nature": "temporary",
            "confidence": 0.92,
            "recovery_direction": "retry",
        },

        "network_error": {
            "root_cause": "Payment network connectivity failure",
            "cause_category": "BANK_OR_NETWORK",
            "nature": "temporary",
            "confidence": 0.90,
            "recovery_direction": "retry",
        },

        "authentication_failure": {
            "root_cause": "Payment authentication failed",
            "cause_category": "AUTHENTICATION",
            "nature": "potentially_persistent",
            "confidence": 0.88,
            "recovery_direction": "customer_action",
        },

        "insufficient_funds": {
            "root_cause": "Insufficient customer funds",
            "cause_category": "CUSTOMER_FUNDS",
            "nature": "potentially_persistent",
            "confidence": 0.94,
            "recovery_direction": "alternate_payment",
        },

        "expired_card": {
            "root_cause": "Payment card has expired",
            "cause_category": "PAYMENT_INSTRUMENT",
            "nature": "persistent",
            "confidence": 0.98,
            "recovery_direction": "alternate_payment",
        },

        "bank_declined": {
            "root_cause": "Bank declined the payment",
            "cause_category": "BANK_DECLINE",
            "nature": "potentially_persistent",
            "confidence": 0.91,
            "recovery_direction": "alternate_payment",
        },
    }


    # ========================================================
    # ATTEMPT ANALYSIS
    # ========================================================

    def _adjust_for_attempts(
        self,
        base_rule,
        attempt_number
    ):
        """
        Repeated failures provide evidence that a problem
        may be persistent rather than temporary.
        """

        rule = base_rule.copy()

        if attempt_number >= 3:

            if rule["nature"] == "temporary":
                rule["nature"] = "persistent"

            rule["confidence"] = min(
                rule["confidence"] + 0.03,
                0.99
            )

        elif attempt_number == 2:

            if rule["nature"] == "temporary":
                rule["nature"] = "potentially_persistent"

        return rule


    # ========================================================
    # RECOVERY DIRECTION
    # ========================================================

    def _determine_recovery_direction(
        self,
        rule,
        attempt_number,
        amount
    ):
        """
        Determine the broad recovery strategy.

        This is NOT the final recovery action.
        The Decision Engine will make that decision later.
        """

        direction = rule[
            "recovery_direction"
        ]

        # High-value transactions should be escalated
        # rather than automatically retried.
        if amount > 50000:
            return "escalate"

        # Third attempt should not trigger another blind retry.
        if attempt_number >= 3:

            if direction == "retry":
                return "escalate"

            return direction

        return direction


    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(self, transaction):

        transaction_id = transaction.get(
            "transaction_id"
        )

        failure_reason = transaction.get(
            "failure_reason"
        )

        attempt_number = int(
            transaction.get(
                "attempt_number",
                1
            )
        )

        amount = float(
            transaction.get(
                "amount",
                0
            )
        )

        # ----------------------------------------------------
        # Unknown failure reason
        # ----------------------------------------------------

        if failure_reason not in self.FAILURE_RULES:

            return {

                "transaction_id":
                    transaction_id,

                "root_cause":
                    "Unknown payment failure",

                "cause_category":
                    "UNKNOWN",

                "nature":
                    "unknown",

                "confidence":
                    0.50,

                "recommended_direction":
                    "escalate",

                "explanation":
                    [
                        "Failure reason is not recognized.",
                        "Manual investigation is recommended."
                    ],
            }

        # ----------------------------------------------------
        # Get base rule.
        # ----------------------------------------------------

        base_rule = self.FAILURE_RULES[
            failure_reason
        ]

        rule = self._adjust_for_attempts(
            base_rule,
            attempt_number
        )

        # ----------------------------------------------------
        # Determine recovery direction.
        # ----------------------------------------------------

        recovery_direction = (
            self._determine_recovery_direction(
                rule,
                attempt_number,
                amount
            )
        )

        # ----------------------------------------------------
        # Build explanation.
        # ----------------------------------------------------

        explanation = []

        explanation.append(
            f"Failure reason: {failure_reason}."
        )

        explanation.append(
            f"Root cause identified as "
            f"{rule['root_cause']}."
        )

        explanation.append(
            f"Cause is classified as "
            f"{rule['nature']}."
        )

        explanation.append(
            f"Current attempt number: "
            f"{attempt_number}."
        )

        if attempt_number >= 3:

            explanation.append(
                "Repeated payment failures increase "
                "the likelihood of a persistent issue."
            )

        if amount > 50000:

            explanation.append(
                "High transaction value requires "
                "additional control before automated recovery."
            )

        explanation.append(
            f"Recommended recovery direction: "
            f"{recovery_direction}."
        )

        return {

            "transaction_id":
                transaction_id,

            "root_cause":
                rule["root_cause"],

            "cause_category":
                rule["cause_category"],

            "nature":
                rule["nature"],

            "confidence":
                round(
                    rule["confidence"],
                    4
                ),

            "recommended_direction":
                recovery_direction,

            "explanation":
                explanation,
        }