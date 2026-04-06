"""ML prediction helpers for Priority Care triage model."""

import os
import pickle
from typing import Any

import numpy as np

# Path to the trained scikit-learn model pickle
MODEL_PATH = os.path.join(os.path.dirname(__file__), "triage_model.pkl")

# Feature columns in the order the model was trained on
FEATURE_COLUMNS = ["age", "pain_level", "resp_rate", "heart_rate", "oxygen_sat"]

# Mapping numeric prediction to triage label string
LABEL_MAP = {0: "GREEN", 1: "YELLOW", 2: "RED"}

# Suggested actions per triage level
ACTION_MAP = {
    "RED": "Immediate assessment — notify doctor now",
    "YELLOW": "Urgent — assess within 30 minutes",
    "GREEN": "Non-urgent — standard queue",
}

_model: Any = None  # Cached model instance


def load_model() -> Any | None:
    """Load the scikit-learn model from disk; return None if unavailable."""
    global _model
    if _model is not None:
        return _model
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        return _model
    except Exception as exc:
        print(f"[predict] Warning: could not load model — {exc}")
        return None


def preprocess(form_data: dict) -> np.ndarray:
    """Convert form data dict to a feature array matching model column order.

    Missing optional vitals default to clinically typical values so the
    model never receives NaN inputs.
    """
    defaults = {
        "age": 35,
        "pain_level": 0,
        "resp_rate": 16,
        "heart_rate": 72,
        "oxygen_sat": 98.0,
    }
    row = []
    for col in FEATURE_COLUMNS:
        val = form_data.get(col)
        try:
            row.append(float(val) if val not in (None, "", "null") else defaults[col])
        except (ValueError, TypeError):
            row.append(defaults[col])
    return np.array([row])


def _rule_based_predict(form_data: dict) -> dict:
    """Fallback rule-based triage when no ML model is available.

    Rules mirror clinical triage thresholds used in the Phase 2 mock-up:
      RED    — pain ≥ 8  OR resp_rate ≥ 25  OR oxygen_sat ≤ 94
      YELLOW — pain ≥ 5  OR resp_rate ≥ 20
      GREEN  — everything else
    """
    try:
        pain = float(form_data.get("pain_level", 0) or 0)
        resp = float(form_data.get("resp_rate", 16) or 16)
        spo2 = float(form_data.get("oxygen_sat", 98) or 98)
    except (ValueError, TypeError):
        pain, resp, spo2 = 0, 16, 98

    if pain >= 8 or resp >= 25 or spo2 <= 94:
        label = "RED"
        confidence = 0.90
    elif pain >= 5 or resp >= 20:
        label = "YELLOW"
        confidence = 0.82
    else:
        label = "GREEN"
        confidence = 0.88

    # Determine which factor drove the result
    top_factors = []
    if pain >= 8:
        top_factors.append("pain_level")
    if resp >= 25:
        top_factors.append("resp_rate")
    if spo2 <= 94:
        top_factors.append("oxygen_sat")
    if not top_factors:
        if pain >= 5:
            top_factors.append("pain_level")
        if resp >= 20:
            top_factors.append("resp_rate")
    if not top_factors:
        top_factors = ["pain_level", "age", "heart_rate"]
    # Pad to 3 factors
    extras = [c for c in FEATURE_COLUMNS if c not in top_factors]
    top_factors = (top_factors + extras)[:3]

    return {
        "label": label,
        "confidence": round(confidence, 2),
        "suggested_action": ACTION_MAP[label],
        "top_factors": top_factors,
        "method": "rule_based",
    }


def predict(form_data: dict) -> dict:
    """Run triage prediction, falling back to rule-based if model is absent.

    Args:
        form_data: Dict with keys age, pain_level, resp_rate, heart_rate,
                   oxygen_sat (all optional except age and pain_level).

    Returns:
        Dict with label, confidence, suggested_action, top_factors, method.

    Raises:
        RuntimeError: If prediction fails for any reason (caller should catch).
    """
    model = load_model()

    if model is None:
        # No model file present — use clinical rule fallback
        return _rule_based_predict(form_data)

    try:
        features = preprocess(form_data)
        raw_label = model.predict(features)[0]

        # Handle models that output numeric or string labels
        if isinstance(raw_label, (int, np.integer)):
            label = LABEL_MAP.get(int(raw_label), "GREEN")
        else:
            label = str(raw_label).upper()
            if label not in ("RED", "YELLOW", "GREEN"):
                label = "GREEN"

        # Confidence from predict_proba if available
        confidence = 0.80
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            confidence = round(float(max(proba)), 2)

        # Top feature importances (works for tree-based models)
        top_factors = FEATURE_COLUMNS[:3]  # sensible default
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            sorted_idx = np.argsort(importances)[::-1]
            top_factors = [FEATURE_COLUMNS[i] for i in sorted_idx[:3]]

        return {
            "label": label,
            "confidence": confidence,
            "suggested_action": ACTION_MAP.get(label, "Assess patient"),
            "top_factors": top_factors,
            "method": "ml_model",
        }

    except Exception as exc:
        # If ML fails unexpectedly, fall back to rules rather than crash
        print(f"[predict] ML prediction error ({exc}); using rule-based fallback")
        return _rule_based_predict(form_data)
