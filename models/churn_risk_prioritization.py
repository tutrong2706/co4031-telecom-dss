"""Churn Risk Scoring & Retention Prioritization.

This is a decision layer on top of the churn classifier, not an independent
predictive model. It ranks customers using churn probability, monthly value,
contract opportunity and service opportunity.
"""

import json
import math
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

from utils import EVAL_DIR, MODEL_DIR, build_preprocessor, load_feature_store, prepare_data_for_churn


MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.pkl")
SCORE_PATH = os.path.join(EVAL_DIR, "churn_priority_scores.csv")
METRICS_PATH = os.path.join(EVAL_DIR, "churn_priority_metrics.csv")
CONFIG_PATH = os.path.join(MODEL_DIR, "churn_priority_config.json")

WEIGHTS = {
    "churn_risk": 0.80,
    "monthly_value": 0.12,
    "contract_opportunity": 0.04,
    "service_opportunity": 0.04,
}
CONTRACT_OPPORTUNITY = {
    "Month-to-month": 1.0,
    "One year": 0.6,
    "Two year": 0.3,
}


def _min_max_scale(values):
    values = values.astype(float)
    value_range = values.max() - values.min()
    if value_range == 0:
        return np.zeros(len(values))
    return (values - values.min()) / value_range


def build_priority_scores(df, churn_probability):
    monthly_value = _min_max_scale(df["monthly_charges"])
    contract_opportunity = df["contract_type"].map(CONTRACT_OPPORTUNITY).fillna(0.5)
    max_addons = max(float(df["total_active_addons"].max()), 1.0)
    service_opportunity = 1.0 - df["total_active_addons"].astype(float) / max_addons

    priority_score = 100 * (
        WEIGHTS["churn_risk"] * churn_probability
        + WEIGHTS["monthly_value"] * monthly_value
        + WEIGHTS["contract_opportunity"] * contract_opportunity
        + WEIGHTS["service_opportunity"] * service_opportunity
    )

    result = df[[
        "customer_id", "monthly_charges", "contract_type",
        "internet_service_type", "total_active_addons", "churn_flag",
    ]].copy()
    result["churn_probability"] = churn_probability
    result["monthly_value_score"] = monthly_value
    result["contract_opportunity_score"] = contract_opportunity
    result["service_opportunity_score"] = service_opportunity
    result["priority_score"] = priority_score
    result["risk_tier"] = pd.cut(
        result["churn_probability"],
        bins=[-np.inf, 0.30, 0.50, 0.70, np.inf],
        labels=["Low", "Medium", "High", "Critical"],
    ).astype(str)
    result["priority_rank"] = result["priority_score"].rank(
        ascending=False, method="first"
    ).astype(int)
    result["priority_percentile"] = (
        1 - (result["priority_rank"] - 1) / len(result)
    )
    result["top_10_percent"] = result["priority_rank"] <= math.ceil(len(result) * 0.10)
    return result.sort_values("priority_rank")


def evaluate_at_k(y_true, priority_scores, fractions=(0.05, 0.10, 0.20)):
    y_true = np.asarray(y_true).astype(int)
    priority_scores = np.asarray(priority_scores)
    prevalence = y_true.mean()
    order = np.argsort(-priority_scores)
    rows = []
    for fraction in fractions:
        top_count = max(1, math.ceil(len(y_true) * fraction))
        selected = order[:top_count]
        captured = int(y_true[selected].sum())
        precision = captured / top_count
        recall = captured / max(int(y_true.sum()), 1)
        rows.append({
            "top_fraction": fraction,
            "top_k_customers": top_count,
            "churn_prevalence": prevalence,
            "churn_captured": captured,
            "precision_at_k": precision,
            "recall_at_k": recall,
            "lift_at_k": precision / prevalence if prevalence else np.nan,
            "campaign_benefit": "unavailable_without_campaign_cost_and_treatment_outcome",
        })
    return pd.DataFrame(rows)


def train_and_evaluate_prioritization():
    df = load_feature_store()
    X_raw, y = prepare_data_for_churn(df)
    churn_model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    oof_pipeline = Pipeline([
        ("preprocessor", clone(preprocessor)),
        ("model", clone(churn_model)),
    ])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_probability = cross_val_predict(
        oof_pipeline,
        X_raw,
        y,
        cv=cv,
        method="predict_proba",
        n_jobs=-1,
    )[:, 1]
    oof_scores = build_priority_scores(df, oof_probability)
    metrics = evaluate_at_k(
        y,
        oof_scores.sort_index()["priority_score"].to_numpy(),
    )
    metrics.to_csv(METRICS_PATH, index=False)

    full_probability = churn_model.predict_proba(
        preprocessor.transform(X_raw)
    )[:, 1]
    scores = build_priority_scores(df, full_probability)
    scores.to_csv(SCORE_PATH, index=False)

    config = {
        "layer_type": "decision_layer_on_churn_model",
        "weights": WEIGHTS,
        "contract_opportunity": CONTRACT_OPPORTUNITY,
        "service_opportunity": "1 - total_active_addons / max_total_active_addons",
        "evaluation": "5-fold out-of-fold probabilities",
        "campaign_benefit": "not_calculated_without_campaign_cost_and_treatment_outcome",
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)

    print(metrics.to_string(index=False))
    print(f"[SAVED] Scores: {SCORE_PATH}")
    print(f"[SAVED] Metrics: {METRICS_PATH}")
    print(f"[SAVED] Config: {CONFIG_PATH}")
    return scores, metrics


if __name__ == "__main__":
    train_and_evaluate_prioritization()
