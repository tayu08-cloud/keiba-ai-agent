import argparse
from pathlib import Path

from keiba_ai_agent.predictor.baseline import BaselinePredictor


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the baseline predictor")
    parser.add_argument("dataset", nargs="?", default="dataset/dataset.csv")
    parser.add_argument("--model-dir", default="models")
    args = parser.parse_args()

    predictor = BaselinePredictor(model_dir=args.model_dir)
    predictor.train(args.dataset)
    print(f"Trained baseline model: {predictor.model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
