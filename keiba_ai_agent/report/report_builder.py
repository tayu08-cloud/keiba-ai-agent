from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class ReportBuilder:
    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir or "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_from_predictions(
        self,
        predictions_path: str | Path,
        openai_comment: str | None = None,
    ) -> list[Path]:
        dataframe = self._read_predictions(predictions_path)
        if "race_id" not in dataframe.columns:
            raise ValueError("predictions.csv must contain a race_id column")

        report_paths: list[Path] = []
        for race_id, race_frame in dataframe.groupby("race_id", sort=True):
            race_number = int(race_frame["race_number"].iloc[0]) if "race_number" in race_frame.columns else 1
            racecourse = str(race_frame["racecourse"].iloc[0]) if "racecourse" in race_frame.columns else "不明"
            race_name = str(race_frame["race_name"].iloc[0]) if "race_name" in race_frame.columns else ""
            report_path = self.output_dir / f"{race_id}.md"
            report_path.write_text(
                self._build_markdown(racecourse, race_number, race_name, race_frame, openai_comment),
                encoding="utf-8",
            )
            report_paths.append(report_path)
        return report_paths

    def _read_predictions(self, predictions_path: str | Path) -> pd.DataFrame:
        path = Path(predictions_path)
        for encoding in ("utf-8", "cp932"):
            try:
                return pd.read_csv(path, encoding=encoding)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(path, encoding="utf-8", engine="python")

    def _build_markdown(
        self,
        racecourse: str,
        race_number: int,
        race_name: str,
        race_frame: pd.DataFrame,
        openai_comment: str | None = None,
    ) -> str:
        ranked = race_frame.sort_values("prediction_score", ascending=False).reset_index(drop=True)
        top_horse = ranked.iloc[0] if len(ranked) > 0 else None
        second_horse = ranked.iloc[1] if len(ranked) > 1 else None
        third_horse = ranked.iloc[2] if len(ranked) > 2 else None
        fourth_horse = ranked.iloc[3] if len(ranked) > 3 else None

        lines: list[str] = []
        lines.append(f"# {racecourse}競馬場 第{race_number}R")
        if race_name:
            lines.append(f"\n{race_name}")
        lines.append("\n◎ 本命")
        if top_horse is not None:
            lines.append(f"- {top_horse['horse_name']} ({top_horse['prediction_score']:.2f})")
        lines.append("\n○ 対抗")
        if second_horse is not None:
            lines.append(f"- {second_horse['horse_name']} ({second_horse['prediction_score']:.2f})")
        lines.append("\n▲ 単穴")
        if third_horse is not None:
            lines.append(f"- {third_horse['horse_name']} ({third_horse['prediction_score']:.2f})")
        lines.append("\n△ 連下")
        if fourth_horse is not None:
            lines.append(f"- {fourth_horse['horse_name']} ({fourth_horse['prediction_score']:.2f})")
        lines.append("\n\n予測スコア表")
        lines.append("\n| 馬番 | 馬名 | 予測スコア |")
        lines.append("| --- | --- | ---: |")
        for _, row in ranked.iterrows():
            horse_name = row.get("horse_name", "")
            score = row.get("prediction_score", 0)
            lines.append(f"| {row.get('horse_id', '')} | {horse_name} | {float(score):.2f} |")

        if openai_comment:
            lines.append("\n### AIコメント")
            lines.append(openai_comment)
        return "\n".join(lines) + "\n"
