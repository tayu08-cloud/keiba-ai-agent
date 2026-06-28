from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Feature:
    feature_id: str | None = None
    feature_name: str | None = None
    feature_value: float | int | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_name": self.feature_name,
            "feature_value": self.feature_value,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Feature":
        return cls(
            feature_id=payload.get("feature_id"),
            feature_name=payload.get("feature_name"),
            feature_value=payload.get("feature_value"),
            source=payload.get("source"),
        )
