import logging
import sys
import time
from typing import Any

from keiba_ai_agent.collector.jvlink_client import JVLinkClient, JVLinkError
from keiba_ai_agent.database import KeibaDatabase, RawRecordRepository
from keiba_ai_agent.parser.jg_parser import parse_jg_record


def run_read_loop(
    client: JVLinkClient,
    data_spec: str,
    from_time: str,
    option: int,
    save_to_db: bool,
    max_records: int,
    retry_wait_seconds: float = 1.0,
    database_path: str | None = None,
) -> int:
    if max_records <= 0:
        return 0

    if save_to_db:
        database = KeibaDatabase(db_path=database_path or "keiba.db")
        repo = RawRecordRepository(database)
    else:
        repo = None

    client.initialize()
    client.open(data_spec=data_spec, from_time=from_time, option=option)

    saved_count = 0
    try:
        for _ in range(max_records):
            while True:
                try:
                    result = client.read()
                except JVLinkError as exc:
                    if exc.code == -3:
                        logger = logging.getLogger(__name__)
                        logger.warning("JVRead returned -3; retrying in %.1fs", retry_wait_seconds)
                        time.sleep(retry_wait_seconds)
                        continue
                    raise

                if result.return_code == 0:
                    logging.info("JVRead reached EOF")
                    return saved_count

                if result.return_code == -3:
                    logging.warning("JVRead returned -3; retrying in %.1fs", retry_wait_seconds)
                    time.sleep(retry_wait_seconds)
                    continue

                if not result.has_data:
                    continue

                if result.data.startswith("JG"):
                    parsed = parse_jg_record(result.data)
                    if repo is not None:
                        repo.save(
                            {
                                "raw": parsed["raw"],
                                "record_type": parsed["record_type"],
                                "filename": result.filename,
                                "return_code": result.return_code,
                            }
                        )
                        saved_count += 1

                print("=== JV-Link raw data ===")
                print(f"filename: {result.filename}")
                print(f"return_code: {result.return_code}")
                print(result.data)
                break
    finally:
        client.close()

    print(f"Saved {saved_count} records to SQLite.")
    return saved_count


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    data_spec = sys.argv[1] if len(sys.argv) >= 2 else "RACE"
    from_time = sys.argv[2] if len(sys.argv) >= 3 else "20240101000000"
    option = int(sys.argv[3]) if len(sys.argv) >= 4 else 1
    save_to_db = len(sys.argv) >= 5 and sys.argv[4].lower() in {"1", "true", "yes", "save"}
    max_records = int(sys.argv[5]) if len(sys.argv) >= 6 else 1

    print("=== JV-Link raw read test ===")
    print(f"data_spec={data_spec}")
    print(f"from_time={from_time}")
    print(f"option={option}")
    print(f"save_to_db={save_to_db}")
    print(f"max_records={max_records}")

    client = JVLinkClient()

    try:
        saved_count = run_read_loop(
            client=client,
            data_spec=data_spec,
            from_time=from_time,
            option=option,
            save_to_db=save_to_db,
            max_records=max_records,
            database_path="keiba.db",
        )
    except JVLinkError as exc:
        logging.exception("JV-Link error: method=%s code=%s", exc.method, exc.code)
        return 1
    except Exception:
        logging.exception("Unexpected error")
        return 1

    print(f"Completed. Saved {saved_count} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
