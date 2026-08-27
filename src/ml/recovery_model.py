import joblib

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler


class RecoveryProbabilityModel:

    def __init__(self):

        self.model = None

        self.numeric_features = [
            "amount",
            "attempt_number",
            "historical_success_rate",
            "customer_tenure_days",
            "avg_transaction_amount",
            "transaction_hour",
        ]

        self.categorical_features = [
            "payment_method",
            "bank",
            "failure_reason",
            "checkout_completed",
            "subscription_flag",
        ]

    def build_pipeline(self):

        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median"
                    )
                ),
                (
                    "scaler",
                    StandardScaler()
                ),
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="most_frequent"
                    )
                ),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore"
                    )
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_pipeline,
                    self.numeric_features,
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    self.categorical_features,
                ),
            ]
        )

        classifier = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )

        self.model = Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor
                ),
                (
                    "classifier",
                    classifier
                ),
            ]
        )

        return self.model

    def fit(self, X, y):

        if self.model is None:
            self.build_pipeline()

        self.model.fit(
            X,
            y
        )

        return self

    def predict_probability(self, X):

        if self.model is None:
            raise ValueError(
                "Model has not been trained."
            )

        return self.model.predict_proba(
            X
        )[:, 1]

    def predict(self, X):

        if self.model is None:
            raise ValueError(
                "Model has not been trained."
            )

        return self.model.predict(
            X
        )

    def save(self, path):

        if self.model is None:
            raise ValueError(
                "Model has not been trained."
            )

        joblib.dump(
            self.model,
            path
        )

    def load(self, path):

        self.model = joblib.load(
            path
        )

        return self