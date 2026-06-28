import sys
from pathlib import Path

from keiba_ai_agent.database import KeibaDatabase, RawRecordRepository


def resolve_db_path(explicit_path: str | None = None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()

    candidates = [
        Path("database/data.db"),
        Path("data.db"),
        Path("keiba.db"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def main() -> int:
    db_path = resolve_db_path(sys.argv[1] if len(sys.argv) > 1 else None)
    database = KeibaDatabase(db_path=db_path)
    repo = RawRecordRepository(database)

    records = repo.list_recent(limit=10)

    if not records:
        print("No raw records found.")
        return 0

    print(f"DB: {db_path}")
    print("Recent raw_records:")
    for record in records:
        preview = (record["raw"] or "")[:50].replace("\n", " ")
        print(
            f"id={record['id']} | record_type={record['record_type']} | "
            f"filename={record['filename']} | return_code={record['return_code']} | "
            f"created_at={record['created_at']} | raw={preview}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
