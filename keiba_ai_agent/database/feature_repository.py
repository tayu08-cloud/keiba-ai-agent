from __future__ import annotations

from typing import Any

from keiba_ai_agent.database.database import BaseRepository, KeibaDatabase
from keiba_ai_agent.models.feature import Feature


class FeatureRepository(BaseRepository):
    def __init__(self, database: KeibaDatabase):
        super().__init__(database)

    def save(self, feature: Feature) -> None:
        self._execute(
            """
            INSERT INTO features (feature_id, feature_name, feature_value, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(feature_id) DO UPDATE SET
                feature_name = excluded.feature_name,
                feature_value = excluded.feature_value,
                source = excluded.source
            """,
            (
                feature.feature_id,
                feature.feature_name,
                feature.feature_value,
                feature.source,
            ),
        )

    def get_by_id(self, feature_id: str) -> dict[str, Any] | None:
        return self._fetch_one(
            "SELECT feature_id, feature_name, feature_value, source FROM features WHERE feature_id = ?",
            (feature_id,),
        )

    def list_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT feature_id, feature_name, feature_value, source
                FROM features ORDER BY feature_id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
