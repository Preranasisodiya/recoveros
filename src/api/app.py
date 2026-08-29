import os
import pandas as pd

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agent.recovery_agent import RecoveryAgent
from src.agent.recovery_state import RecoveryState


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="RecoverOS API",
    description=(
        "Revenue recovery decision and simulation API "
        "for failed payment transactions."
    ),
    version="1.0.0",
)


# ============================================================
# RECOVERY AGENT
# ============================================================

agent = RecoveryAgent()

# ============================================================
# BUSINESS METRICS
# ============================================================

METRICS_FILE = os.path.join(
    "data",
    "business_impact_summary.csv"
)

# ============================================================
# REQUEST MODEL
# ============================================================

class TransactionRequest(BaseModel):
    transaction_id: str

    amount: float = Field(
        gt=0
    )

    failure_reason: str

    payment_method: str

    attempt_number: int = Field(
        ge=1
    )

    historical_success_rate: float = Field(
        ge=0,
        le=1
    )

    customer_tenure_days: int = Field(
        ge=0
    )

    avg_transaction_amount: float = Field(
        ge=0
    )

    transaction_hour: int = Field(
        ge=0,
        le=23
    )

    bank: str

    checkout_completed: bool

    subscription_flag: bool


class RecoveryExecutionRequest(
    TransactionRequest
):
    forced_outcome: Optional[str] = None


# ============================================================
# RESPONSE SERIALIZATION
# ============================================================

def state_to_response(
    state: RecoveryState,
):
    return {
        "transaction_id":
            state.transaction_id,

        "amount":
            state.amount,

        "failure_reason":
            state.failure_reason,

        "payment_method":
            state.payment_method,

        "attempt_number":
            state.attempt_number,

        "risk_score":
            state.risk_score,

        "risk_level":
            state.risk_level,

        "root_cause":
            state.root_cause,

        "cause_category":
            state.cause_category,

        "cause_nature":
            state.cause_nature,

        "root_cause_confidence":
            state.root_cause_confidence,

        "recovery_direction":
            state.recovery_direction,

        "recovery_probability":
            state.recovery_probability,

        "decision":
            state.decision,

        "decision_confidence":
            state.decision_confidence,

        "decision_reason":
            state.decision_reason,

        "status":
            state.status,

        "recovered_amount":
            state.recovered_amount,

        "escalation_required":
            state.escalation_required,

        "escalation_reason":
            state.escalation_reason,

        "actions_taken":
            state.actions_taken,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health"
)
def health_check():

    return {
        "status": "healthy",
        "service": "RecoverOS API",
    }

# ============================================================
# BUSINESS METRICS
# ============================================================

@app.get(
    "/metrics"
)
def get_metrics():

    if not os.path.exists(
        METRICS_FILE
    ):
        raise HTTPException(
            status_code=404,
            detail="Business metrics file not found."
        )

    try:

        metrics_df = pd.read_csv(
            METRICS_FILE
        )

        metrics = {}

        for _, row in metrics_df.iterrows():

            metric_name = row["metric"]

            metric_value = row["value"]

            metrics[
                metric_name
            ] = metric_value

        return {
            "status": "success",
            "metrics": metrics,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

# ============================================================
# TRANSACTIONS
# ============================================================

TRANSACTIONS_FILE = os.path.join(
    "data",
    "recovery_system_evaluation.csv"
)


@app.get(
    "/transactions"
)
def get_transactions():

    if not os.path.exists(
        TRANSACTIONS_FILE
    ):
        raise HTTPException(
            status_code=404,
            detail="Recovery system evaluation file not found."
        )

    try:

        transactions_df = pd.read_csv(
            TRANSACTIONS_FILE
        )

        # Replace NaN values with None
        transactions_df = transactions_df.where(
            pd.notnull(transactions_df),
            None
        )

        return {
            "status": "success",
            "count": len(transactions_df),
            "transactions": (
                transactions_df
                .to_dict(orient="records")
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

# ============================================================
# TRANSACTION DETAIL
# ============================================================

@app.get(
    "/transactions/{transaction_id}"
)
def get_transaction(
    transaction_id: str
):

    if not os.path.exists(
        TRANSACTIONS_FILE
    ):
        raise HTTPException(
            status_code=404,
            detail="Recovery system evaluation file not found."
        )

    try:

        transactions_df = pd.read_csv(
            TRANSACTIONS_FILE
        )

        transaction = transactions_df[
            transactions_df[
                "transaction_id"
            ].astype(str)
            == transaction_id
        ]

        if transaction.empty:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Transaction "
                    f"{transaction_id} not found."
                )
            )

        record = transaction.iloc[
            0
        ].to_dict()

        # Convert NaN values to None
        record = {
            key: (
                None
                if pd.isna(value)
                else value
            )
            for key, value in record.items()
        }

        return {
            "status": "success",
            "transaction": record,
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

# ============================================================
# ANALYZE TRANSACTION
# ============================================================

@app.post(
    "/analyze"
)
def analyze_transaction(
    transaction: TransactionRequest,
):

    try:

        state = agent.process(
            transaction.model_dump()
        )

        return state_to_response(
            state
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# EXECUTE RECOVERY
# ============================================================

@app.post(
    "/recover"
)
def execute_recovery(
    transaction: RecoveryExecutionRequest,
):

    try:

        state = agent.process(
            transaction.model_dump(
                exclude={
                    "forced_outcome"
                }
            )
        )

        state = agent.execute_recovery(
            state,
            forced_outcome=(
                transaction.forced_outcome
            ),
        )

        return state_to_response(
            state
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )