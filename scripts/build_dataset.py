import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from keiba_ai_agent.dataset.dataset_builder import DatasetBuilder


def main() -> int:
    db_path = sys.argv[1] if len(sys.argv) >= 2 else "keiba.db"
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else "dataset"

    builder = DatasetBuilder(database_path=db_path, output_dir=output_dir)
    output_paths = builder.save_dataset()
    print(f"Saved dataset to {output_paths['csv']} and {output_paths['parquet']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
