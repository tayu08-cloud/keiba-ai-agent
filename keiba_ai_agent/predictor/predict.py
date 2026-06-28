import argparse
from pathlib import Path

from keiba_ai_agent.predictor.baseline import BaselinePredictor


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict with the baseline predictor")
    parser.add_argument("dataset", nargs="?", default="dataset/dataset.csv")
    parser.add_argument("--model-dir", default="models")
    args = parser.parse_args()

    predictor = BaselinePredictor(model_dir=args.model_dir)
    probabilities = predictor.predict(args.dataset)
    for index, value in enumerate(probabilities):
        print(f"{index}: {value:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
