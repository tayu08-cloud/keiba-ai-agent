from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

from keiba_ai_agent.predictor.baseline import BaselinePredictor


def evaluate_model(predictor: BaselinePredictor, dataset_path: str | Path) -> dict[str, float]:
    dataframe = pd.read_csv(dataset_path)
    if "label" not in dataframe.columns:
        raise ValueError("evaluation dataset must contain a label column")

    predictions = predictor.predict(dataset_path)
    labels = dataframe["label"].astype(int).to_numpy()
    predicted_labels = [int(score >= 0.5) for score in predictions]

    return {
        "accuracy": float(accuracy_score(labels, predicted_labels)),
        "roc_auc": float(roc_auc_score(labels, predictions)),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate the baseline predictor")
    parser.add_argument("dataset", nargs="?", default="dataset/dataset.csv")
    parser.add_argument("--model-dir", default="models")
    args = parser.parse_args()

    predictor = BaselinePredictor(model_dir=args.model_dir)
    metrics = evaluate_model(predictor, args.dataset)
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
