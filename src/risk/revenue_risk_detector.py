import math


class RevenueRiskDetector:
    """
    Explainable rule-based revenue risk detector.

    The detector evaluates a failed payment using only
    information available before recovery is attempted.

    Output:
        - revenue_at_risk
        - risk_score
        - risk_level
        - recovery_eligible
        - explanation
    """

    FAILURE_SCORES = {
        "bank_timeout": 0.20,
        "network_error": 0.18,
        "authentication_failure": 0.10,
        "bank_declined": 0.08,
        "insufficient_funds": 0.05,
        "expired_card": 0.02,
    }

    def __init__(self):
        pass

    # --------------------------------------------------------
    # Failure contribution
    # --------------------------------------------------------

    def _failure_score(self, failure_reason):
        return self.FAILURE_SCORES.get(
            failure_reason,
            0.05
        )

    # --------------------------------------------------------
    # Customer contribution
    # --------------------------------------------------------

    def _customer_score(self, success_rate):
        """
        Convert historical payment success rate into
        a 0-1 contribution.
        """

        if success_rate is None:
            return 0.50

        return max(
            0.0,
            min(
                float(success_rate),
                1.0
            )
        )

    # --------------------------------------------------------
    # Attempt contribution
    # --------------------------------------------------------

    def _attempt_score(self, attempt_number):

        if attempt_number <= 1:
            return 1.00

        if attempt_number == 2:
            return 0.60

        return 0.20

    # --------------------------------------------------------
    # Transaction value contribution
    # --------------------------------------------------------

    def _amount_score(self, amount):
        """
        Use a logarithmic transformation so that a ₹100,000
        transaction does not completely dominate a ₹5,000
        transaction.
        """

        amount = max(
            float(amount),
            0.0
        )

        if amount == 0:
            return 0.0

        score = (
            math.log10(amount + 1)
            / math.log10(100001)
        )

        return max(
            0.0,
            min(
                score,
                1.0
            )
        )

    # --------------------------------------------------------
    # Checkout contribution
    # --------------------------------------------------------

    def _checkout_score(self, checkout_completed):

        return (
            1.0
            if checkout_completed
            else 0.30
        )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    def _risk_level(self, score):

        if score >= 0.70:
            return "CRITICAL"

        if score >= 0.60:
            return "HIGH"

        if score >= 0.30:
            return "MEDIUM"

        return "LOW"

    # --------------------------------------------------------
    # Main detector
    # --------------------------------------------------------

    def detect(self, transaction):
        """
        Analyze one failed transaction.

        Expected transaction fields:

            transaction_id
            amount
            status
            failure_reason
            payment_method
            attempt_number
            historical_success_rate
            checkout_completed
        """

        transaction_id = transaction.get(
            "transaction_id"
        )

        amount = float(
            transaction.get(
                "amount",
                0
            )
        )

        status = transaction.get(
            "status"
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

        historical_success_rate = float(
            transaction.get(
                "historical_success_rate",
                0.50
            )
        )

        checkout_completed = bool(
            transaction.get(
                "checkout_completed",
                False
            )
        )

        # ----------------------------------------------------
        # Successful transactions are not revenue-at-risk.
        # ----------------------------------------------------

        if status != "failed":

            return {
                "transaction_id": transaction_id,
                "revenue_at_risk": 0.0,
                "risk_score": 0.0,
                "risk_level": "LOW",
                "recovery_eligible": False,
                "explanation": [
                    "Payment is not currently failed."
                ],
            }

        # ----------------------------------------------------
        # Calculate individual factors.
        # ----------------------------------------------------

        failure_score = self._failure_score(
            failure_reason
        )

        customer_score = self._customer_score(
            historical_success_rate
        )

        attempt_score = self._attempt_score(
            attempt_number
        )

        amount_score = self._amount_score(
            amount
        )

        checkout_score = self._checkout_score(
            checkout_completed
        )

        # ----------------------------------------------------
        # Weighted risk score.
        #
        # Customer history and failure characteristics
        # receive the greatest influence.
        # ----------------------------------------------------

        risk_score = (

            0.30 * failure_score

            + 0.30 * customer_score

            + 0.15 * attempt_score

            + 0.15 * amount_score

            + 0.10 * checkout_score
        )

        risk_score = max(
            0.0,
            min(
                risk_score,
                1.0
            )
        )

        risk_level = self._risk_level(
            risk_score
        )

        # ----------------------------------------------------
        # Recovery eligibility.
        #
        # We avoid recovery when the payment has already
        # reached the maximum attempt count.
        # ----------------------------------------------------

        recovery_eligible = (

            risk_score >= 0.30

            and attempt_number < 3

            and amount > 0
        )

        # ----------------------------------------------------
        # Explainability.
        # ----------------------------------------------------

        explanation = []

        explanation.append(
            f"Payment failed due to {failure_reason}."
        )

        explanation.append(
            f"Transaction value is ₹{amount:,.2f}."
        )

        explanation.append(
            f"Customer historical success rate is "
            f"{historical_success_rate:.1%}."
        )

        explanation.append(
            f"Current payment attempt number is "
            f"{attempt_number}."
        )

        if checkout_completed:

            explanation.append(
                "Checkout was completed, indicating "
                "strong payment intent."
            )

        else:

            explanation.append(
                "Checkout was not completed."
            )

        if attempt_number >= 3:

            explanation.append(
                "Maximum automated attempt threshold "
                "has been reached."
            )

        if recovery_eligible:

            explanation.append(
                "Transaction qualifies for recovery "
                "evaluation."
            )

        else:

            explanation.append(
                "Transaction does not qualify for "
                "automated recovery."
            )

        return {
            "transaction_id": transaction_id,
            "revenue_at_risk": round(
                amount,
                2
            ),
            "risk_score": round(
                risk_score,
                4
            ),
            "risk_level": risk_level,
            "recovery_eligible": recovery_eligible,
            "explanation": explanation,
        }