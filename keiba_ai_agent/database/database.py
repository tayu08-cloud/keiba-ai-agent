import sqlite3
from pathlib import Path
from typing import Any


class KeibaDatabase:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or "keiba.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        with schema_path.open("r", encoding="utf-8") as handle:
            schema_sql = handle.read()

        with self.connect() as connection:
            connection.executescript(schema_sql)
            connection.commit()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection


class BaseRepository:
    def __init__(self, database: KeibaDatabase):
        self.database = database

    def _fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(query, params).fetchone()
            if row is None:
                return None
            return dict(row)

    def _execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.database.connect() as connection:
            connection.execute(query, params)
            connection.commit()


class RaceRepository(BaseRepository):
    def save(self, payload: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT OR REPLACE INTO races (
                race_id, race_date, racecourse, race_number, race_name, distance, surface
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("race_id"),
                payload.get("race_date"),
                payload.get("racecourse"),
                payload.get("race_number"),
                payload.get("race_name"),
                payload.get("distance"),
                payload.get("surface"),
            ),
        )

    def get_by_id(self, race_id: str) -> dict[str, Any] | None:
        return self._fetch_one(
            "SELECT race_id, race_date, racecourse, race_number, race_name, distance, surface FROM races WHERE race_id = ?",
            (race_id,),
        )


class HorseRepository(BaseRepository):
    def save(self, payload: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT OR REPLACE INTO horses (horse_id, horse_name)
            VALUES (?, ?)
            """,
            (payload.get("horse_id"), payload.get("horse_name")),
        )

    def get_by_id(self, horse_id: str) -> dict[str, Any] | None:
        return self._fetch_one(
            "SELECT horse_id, horse_name FROM horses WHERE horse_id = ?",
            (horse_id,),
        )


class EntryRepository(BaseRepository):
    def save(self, payload: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT OR REPLACE INTO entries (
                race_id, horse_id, frame_number, horse_number, jockey, trainer, odds, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("race_id"),
                payload.get("horse_id"),
                payload.get("frame_number"),
                payload.get("horse_number"),
                payload.get("jockey"),
                payload.get("trainer"),
                payload.get("odds"),
                payload.get("score"),
            ),
        )

    def get_by_race_and_horse(self, race_id: str, horse_id: str) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT race_id, horse_id, frame_number, horse_number, jockey, trainer, odds, score
            FROM entries WHERE race_id = ? AND horse_id = ?
            """,
            (race_id, horse_id),
        )


class RawRecordRepository(BaseRepository):
    def save(self, payload: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO raw_records (raw, record_type, filename, return_code)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.get("raw"),
                payload.get("record_type"),
                payload.get("filename"),
                payload.get("return_code"),
            ),
        )

    def get_latest(self) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT id, raw, record_type, filename, return_code, created_at
            FROM raw_records ORDER BY id DESC LIMIT 1
            """
        )

    def list_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, raw, record_type, filename, return_code, created_at
                FROM raw_records ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
