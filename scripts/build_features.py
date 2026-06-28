import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from keiba_ai_agent.features.feature_builder import FeatureBuilder


def main() -> int:
    db_path = sys.argv[1] if len(sys.argv) >= 2 else "keiba.db"
    builder = FeatureBuilder(database_path=db_path)
    saved_count = builder.save_features_for_horses()
    print(f"Saved {saved_count} features to SQLite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
