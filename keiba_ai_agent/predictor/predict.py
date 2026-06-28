import argparse
from pathlib import Path

from keiba_ai_agent.predictor.baseline import BaselinePredictor


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict with the baseline predictor")
    parser.add_argument("dataset", nargs="?", default="dataset/dataset.csv")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--output", default="predictions.csv")
    args = parser.parse_args()

    predictor = BaselinePredictor(model_dir=args.model_dir)
    predictions = predictor.predict_and_save(args.dataset, args.output)
    for index, row in predictions.iterrows():
        print(f"{index}: {row['prediction_score']:.4f} -> {row['predicted_label']}")
    print(f"Saved predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
