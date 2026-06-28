import logging
import time
from pathlib import Path
from typing import Any

from keiba_ai_agent.collector.jvlink_client import JVLinkClient, JVLinkError
from keiba_ai_agent.database import KeibaDatabase, HorseRepository, RawRecordRepository
from keiba_ai_agent.parser.jg_parser import parse_jg_record


class DataIngestionService:
    """Coordinate raw-data fetch, parsing, and SQLite persistence."""

    def __init__(
        self,
        client: JVLinkClient | None = None,
        database_path: str | Path | None = None,
    ) -> None:
        self.client = client or JVLinkClient()
        self.database_path = Path(database_path or "keiba.db")
        self.logger = logging.getLogger(__name__)

    def ingest(
        self,
        data_spec: str,
        from_time: str,
        option: int,
        save_to_db: bool = True,
        max_records: int = 1,
        retry_wait_seconds: float = 1.0,
    ) -> int:
        if max_records <= 0:
            return 0

        if save_to_db:
            database = KeibaDatabase(db_path=self.database_path)
            raw_repo = RawRecordRepository(database)
            horse_repo = HorseRepository(database)
        else:
            raw_repo = None
            horse_repo = None

        self.client.initialize()
        self.client.open(data_spec=data_spec, from_time=from_time, option=option)

        saved_count = 0
        try:
            for _ in range(max_records):
                while True:
                    try:
                        result = self.client.read()
                    except JVLinkError as exc:
                        if exc.code == -3:
                            self.logger.warning("JVRead returned -3; retrying in %.1fs", retry_wait_seconds)
                            time.sleep(retry_wait_seconds)
                            continue
                        raise

                    if result.return_code == 0:
                        self.logger.info("JVRead reached EOF")
                        return saved_count

                    if result.return_code == -3:
                        self.logger.warning("JVRead returned -3; retrying in %.1fs", retry_wait_seconds)
                        time.sleep(retry_wait_seconds)
                        continue

                    if not result.has_data:
                        continue

                    if result.data.startswith("JG"):
                        parsed = parse_jg_record(result.data)
                        if raw_repo is not None:
                            raw_repo.save(
                                {
                                    "raw": parsed.raw,
                                    "record_type": parsed.record_type,
                                    "filename": result.filename,
                                    "return_code": result.return_code,
                                }
                            )
                            horse_repo.upsert_horse_from_model(parsed)
                            saved_count += 1

                    break
        finally:
            self.client.close()

        return saved_count
