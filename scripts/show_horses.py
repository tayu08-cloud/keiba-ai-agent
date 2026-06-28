import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from keiba_ai_agent.database import KeibaDatabase, HorseRepository


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
    repo = HorseRepository(database)

    with database.connect() as connection:
        rows = connection.execute(
            "SELECT horse_id, horse_name FROM horses ORDER BY rowid DESC LIMIT 50"
        ).fetchall()

    if not rows:
        print("No horses found.")
        return 0

    print(f"DB: {db_path}")
    print("Recent horses:")
    for row in rows:
        print(f"horse_id={row['horse_id']} | horse_name={row['horse_name']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
