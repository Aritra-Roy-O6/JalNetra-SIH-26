"""PFZ model registry and prediction service."""

from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path
from typing import Any
import warnings

import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning

MODEL_FEATURES = (
    "sst", "chlorophyll", "chlorophyll_log", "ssh", "ssh_anomaly",
    "current_u", "current_v", "wind_speed", "wind_direction_deg",
    "depth", "distance_to_coast_km",
)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "pfz_rf_no_gradient_no_currentspeed.pkl"


@lru_cache(maxsize=1)
def load_pfz_model() -> Any:
    if not MODEL_PATH.is_file():
        raise RuntimeError(f"PFZ model artifact not found: {MODEL_PATH}")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InconsistentVersionWarning)
        model = joblib.load(MODEL_PATH)
    missing = [name for name in MODEL_FEATURES if name not in getattr(model, "feature_names_in_", MODEL_FEATURES)]
    if missing or getattr(model, "n_features_in_", len(MODEL_FEATURES)) != len(MODEL_FEATURES):
        raise RuntimeError(f"PFZ model feature contract mismatch; missing={missing}")
    model._jalnetra_runtime_error = next(
        (str(warning.message) for warning in caught if issubclass(warning.category, InconsistentVersionWarning)),
        None,
    )
    return model


def predict_pfz(features: dict[str, float], model: Any | None = None) -> dict:
    loaded_model: Any = model or load_pfz_model()
    if error := getattr(loaded_model, "_jalnetra_runtime_error", None):
        raise RuntimeError(f"PFZ model artifact is incompatible with the installed scikit-learn runtime: {error}")
    missing = [name for name in MODEL_FEATURES if name not in features]
    aligned: dict[str, float] = {}
    invalid = []
    for name in MODEL_FEATURES:
        if name not in features:
            continue
        try:
            value = float(features[name])
        except (TypeError, ValueError):
            invalid.append(name)
            continue
        if not math.isfinite(value):
            invalid.append(name)
            continue
        aligned[name] = value
    if missing or invalid:
        raise ValueError(f"PFZ feature contract failed; missing={missing}, invalid={invalid}")
    row = pd.DataFrame([[aligned[name] for name in MODEL_FEATURES]], columns=MODEL_FEATURES)
    label = int(loaded_model.predict(row)[0])
    confidence = float(loaded_model.predict_proba(row)[0][label]) if hasattr(loaded_model, "predict_proba") else float(label)
    return {"label": label, "confidence_score": round(confidence, 4), "features": aligned}


def current_pfz_prediction(
    latitude: float | None = None,
    longitude: float | None = None,
    distance_to_coast_km: float | None = None,
    model: Any | None = None,
) -> dict:
    """Score live provider values only when the complete model contract is met."""
    if latitude is None or longitude is None:
        return {"available": False, "error": "Select a map location before requesting a PFZ prediction.", "providers": {}}

    from app.services.marine_data import live_pfz_features

    try:
        snapshot = live_pfz_features(latitude, longitude, distance_to_coast_km)
    except Exception as error:
        return {
            "available": False,
            "error": f"Live PFZ data is temporarily unavailable: {error}",
            "providers": {},
            "warnings": [],
            "location": {"latitude": latitude, "longitude": longitude},
        }
    missing = [name for name in MODEL_FEATURES if name not in snapshot["features"]]
    if missing:
        return {
            "available": False,
            "error": "A current PFZ prediction needs complete observed features.",
            "missing_features": missing,
            "providers": snapshot["providers"],
            "errors": snapshot["errors"],
            "warnings": snapshot["warnings"],
            "location": snapshot["location"],
        }
    try:
        prediction = predict_pfz(snapshot["features"], model)
    except RuntimeError as error:
        return {"available": False, "error": str(error), "providers": snapshot["providers"], "warnings": snapshot["warnings"], "location": snapshot["location"]}
    return {"available": True, "providers": snapshot["providers"], "warnings": snapshot["warnings"], "location": snapshot["location"], **prediction}
