from __future__ import annotations

from typing import Any

from keiba_ai_agent.database import FeatureRepository, KeibaDatabase
from keiba_ai_agent.models import Feature


class FeatureBuilder:
    """Build a minimal set of horse features from the current domain model."""

    def __init__(self, database_path: str | None = None):
        self.database = KeibaDatabase(db_path=database_path)
        self.feature_repo = FeatureRepository(self.database)

    def build_from_horse(self, horse_id: str | None, horse_name: str | None) -> list[Feature]:
        features: list[Feature] = []
        if horse_name is not None:
            features.append(
                Feature(
                    feature_id=f"{horse_id or 'unknown'}:horse_name_length",
                    feature_name="horse_name_length",
                    feature_value=len(horse_name),
                    source="horse",
                )
            )
        features.append(
            Feature(
                feature_id=f"{horse_id or 'unknown'}:has_horse_id",
                feature_name="has_horse_id",
                feature_value=1 if bool(horse_id) else 0,
                source="horse",
            )
        )
        return features

    def save_features_for_horses(self) -> int:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT horse_id, horse_name FROM horses").fetchall()

        saved_count = 0
        for row in rows:
            horse_id = row["horse_id"]
            horse_name = row["horse_name"]
            for feature in self.build_from_horse(horse_id, horse_name):
                self.feature_repo.save(feature)
                saved_count += 1

        return saved_count
