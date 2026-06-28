from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EntryFeature:
    race_id: str | None = None
    horse_id: str | None = None
    feature_name: str | None = None
    feature_value: float | int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "race_id": self.race_id,
            "horse_id": self.horse_id,
            "feature_name": self.feature_name,
            "feature_value": self.feature_value,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EntryFeature":
        return cls(
            race_id=payload.get("race_id"),
            horse_id=payload.get("horse_id"),
            feature_name=payload.get("feature_name"),
            feature_value=payload.get("feature_value"),
        )
