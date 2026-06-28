from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

try:  # pragma: no cover - optional dependency
    import lightgbm as lgb
except ImportError:  # pragma: no cover - optional dependency
    lgb = None


class BaselinePredictor:
    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir or "models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / "baseline_model.joblib"
        self.model: Any = None

    def _feature_columns(self) -> list[str]:
        return ["horse_name_length", "has_horse_id"]

    def _load_dataset(self, dataset_path: str | Path) -> pd.DataFrame:
        dataframe = pd.read_csv(dataset_path)
        if "label" not in dataframe.columns:
            raise ValueError("dataset must contain a label column")
        return dataframe[[*self._feature_columns(), "label"]].copy()

    def train(self, dataset_path: str | Path) -> Any:
        dataframe = self._load_dataset(dataset_path)
        features = dataframe[self._feature_columns()]
        labels = dataframe["label"]

        if lgb is not None:
            model = lgb.LGBMClassifier(n_estimators=50, random_state=42)
        else:
            model = RandomForestClassifier(n_estimators=50, random_state=42)

        model.fit(features, labels)
        self.model = model
        self._save_model(model)
        return model

    def predict(self, dataset_path: str | Path) -> list[float]:
        dataframe = pd.read_csv(dataset_path)
        if self.model is None:
            self.model = self._load_model()
        features = dataframe[self._feature_columns()]
        return [float(value) for value in self.model.predict_proba(features)[:, 1]]

    def _save_model(self, model: Any) -> None:
        with self.model_path.open("wb") as handle:
            pickle.dump(model, handle)

    def _load_model(self) -> Any:
        if not self.model_path.exists():
            raise FileNotFoundError(f"model not found: {self.model_path}")
        with self.model_path.open("rb") as handle:
            return pickle.load(handle)
