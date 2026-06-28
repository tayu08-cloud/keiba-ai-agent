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
            "SELECT feature_id, feature_name, feature_value FROM features ORDER BY rowid DESC LIMIT 50"
        ).fetchall()

    if not rows:
        print("No features found.")
        return 0

    print(f"DB: {db_path}")
    print("Recent features:")
    for row in rows:
        feature_id = row["feature_id"]
        horse_id = feature_id.split(":", 1)[0] if feature_id else ""
        print(
            f"horse_id={horse_id} | feature_name={row['feature_name']} | feature_value={row['feature_value']} | created_at=unknown"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
