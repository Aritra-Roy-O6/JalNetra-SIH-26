"""Train and atomically export JalNetra's PFZ RandomForest artifact."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

FEATURES = (
    "sst", "chlorophyll", "chlorophyll_log", "ssh", "ssh_anomaly",
    "current_u", "current_v", "wind_speed", "wind_direction_deg",
    "depth", "distance_to_coast_km",
)


def read_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError("Dataset must be a CSV or Parquet file.")


def train(dataset: Path, target: str, output: Path) -> float:
    frame = read_dataset(dataset)
    required = [*FEATURES, target]
    missing = [column for column in required if column not in frame]
    if missing:
        raise ValueError(f"Training data is missing columns: {missing}")

    features = frame.loc[:, FEATURES].apply(pd.to_numeric, errors="coerce")
    labels = frame[target]
    valid = features.notna().all(axis=1) & labels.notna()
    features, labels = features.loc[valid], labels.loc[valid]
    if len(features) < 20 or labels.nunique() < 2:
        raise ValueError("Need at least 20 complete rows and two target classes.")

    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.2, random_state=42, stratify=labels,
    )
    model = RandomForestClassifier(
        n_estimators=500, random_state=42, n_jobs=-1, class_weight="balanced_subsample",
    ).fit(train_x, train_y)
    score = float(model.score(test_x, test_y))

    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=output.parent, suffix=".pkl", delete=False)
    temporary = Path(handle.name)
    handle.close()
    try:
        joblib.dump(model, temporary)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", default="pfz_label")
    parser.add_argument("--output", type=Path, default=Path("models/pfz_rf_no_gradient_no_currentspeed.pkl"))
    args = parser.parse_args()
    score = train(args.dataset, args.target, args.output)
    print(f"exported={args.output} holdout_accuracy={score:.4f}")


if __name__ == "__main__":
    main()
