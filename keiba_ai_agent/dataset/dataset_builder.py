from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover - depends on runtime environment
    pd = None

from keiba_ai_agent.database import KeibaDatabase


class DatasetBuilder:
    def __init__(self, database_path: str | Path | None = None, output_dir: str | Path | None = None):
        self.database = KeibaDatabase(db_path=database_path)
        self.output_dir = Path(output_dir or "dataset")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_dataset(self) -> Any:
        if pd is None:
            raise RuntimeError("pandas is required for dataset building; use the .venv environment")

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT h.horse_id, h.horse_name, f.feature_name, f.feature_value
                FROM horses AS h
                LEFT JOIN features AS f ON f.feature_id LIKE h.horse_id || ':%'
                ORDER BY h.horse_id, f.feature_name
                """
            ).fetchall()

        frame = pd.DataFrame([dict(row) for row in rows])
        if frame.empty:
            return pd.DataFrame(columns=["horse_id", "horse_name", "feature_name", "feature_value"])

        pivoted = frame.pivot_table(
            index=["horse_id", "horse_name"],
            columns="feature_name",
            values="feature_value",
            aggfunc="first",
            fill_value=None,
        ).reset_index()
        return pivoted

    def save_dataset(self, output_dir: str | Path | None = None) -> dict[str, Path]:
        output_dir_path = Path(output_dir or self.output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        dataframe = self.build_dataset()
        csv_path = output_dir_path / "dataset.csv"
        parquet_path = output_dir_path / "dataset.parquet"

        dataframe.to_csv(csv_path, index=False)
        try:
            dataframe.to_parquet(parquet_path, index=False)
        except ImportError:
            parquet_path = output_dir_path / "dataset.parquet"
            if parquet_path.exists():
                parquet_path.unlink()
            raise RuntimeError("pyarrow is required to write parquet files")

        return {"csv": csv_path, "parquet": parquet_path}
