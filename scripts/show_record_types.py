import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from keiba_ai_agent.database import KeibaDatabase


def resolve_db_path(explicit_path: str | None = None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()

    candidates = [
        PROJECT_ROOT / "database" / "data.db",
        PROJECT_ROOT / "data.db",
        PROJECT_ROOT / "keiba.db",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[-1]


def main() -> int:
    db_path = resolve_db_path(sys.argv[1] if len(sys.argv) > 1 else None)
    database = KeibaDatabase(db_path=db_path)

    with database.connect() as connection:
        rows = connection.execute(
            "SELECT record_type, COUNT(*) AS count FROM raw_records GROUP BY record_type ORDER BY count DESC, record_type"
        ).fetchall()

    if not rows:
        print("No raw records found.")
        return 0

    print(f"DB: {db_path}")
    for row in rows:
        print(f"{row['record_type']}: {row['count']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
