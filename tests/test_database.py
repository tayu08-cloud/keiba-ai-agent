import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from keiba_ai_agent.collector.jvlink_read_test import run_read_loop
from keiba_ai_agent.database import (
    KeibaDatabase,
    RaceRepository,
    HorseRepository,
    EntryRepository,
    RawRecordRepository,
)
from keiba_ai_agent.features.feature_builder import FeatureBuilder
from keiba_ai_agent.models import HorseFeature, RaceFeature, EntryFeature, Feature, FeatureRepository
from keiba_ai_agent.parser.jg_parser import Horse
from keiba_ai_agent.services import DataIngestionService


def test_repositories_persist_race_horse_and_entry(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)

    race_repo = RaceRepository(database)
    horse_repo = HorseRepository(database)
    entry_repo = EntryRepository(database)

    race = {
        "race_id": "20250628-01",
        "race_date": "2025-06-28",
        "racecourse": "東京",
        "race_number": 1,
        "race_name": "東京メイプル賞",
        "distance": 1800,
        "surface": "芝",
    }
    horse = {
        "horse_id": "horse-001",
        "horse_name": "サクラノリュウ",
    }
    entry = {
        "race_id": race["race_id"],
        "horse_id": horse["horse_id"],
        "frame_number": 1,
        "horse_number": 2,
        "jockey": "田中",
        "trainer": "佐藤",
        "odds": 6.2,
        "score": 80,
    }

    race_repo.save(race)
    horse_repo.save(horse)
    entry_repo.save(entry)

    saved_race = race_repo.get_by_id(race["race_id"])
    saved_horse = horse_repo.get_by_id(horse["horse_id"])
    saved_entry = entry_repo.get_by_race_and_horse(race["race_id"], horse["horse_id"])

    assert saved_race is not None
    assert saved_race["race_name"] == race["race_name"]
    assert saved_race["racecourse"] == race["racecourse"]

    assert saved_horse is not None
    assert saved_horse["horse_name"] == horse["horse_name"]

    assert saved_entry is not None
    assert saved_entry["horse_number"] == entry["horse_number"]
    assert saved_entry["jockey"] == entry["jockey"]


def test_raw_record_repository_persists_parsed_jg_payload(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    repo = RawRecordRepository(database)

    payload = {
        "raw": "JG12025062720250628020105002022100614ハーフェン",
        "record_type": "JG",
        "filename": "sample.txt",
        "return_code": 1,
    }

    repo.save(payload)
    latest = repo.get_latest()
    recent = repo.list_recent(limit=10)

    assert latest is not None
    assert latest["raw"] == payload["raw"]
    assert latest["record_type"] == payload["record_type"]
    assert latest["filename"] == payload["filename"]
    assert latest["return_code"] == payload["return_code"]
    assert latest["created_at"]
    assert len(recent) == 1
    assert recent[0]["id"] == latest["id"]


def test_run_read_loop_retries_on_return_code_minus_three_and_saves_records(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    client = Mock()
    results = [
        type("Result", (), {"return_code": -3, "has_data": False, "data": "", "filename": ""})(),
        type("Result", (), {"return_code": 1, "has_data": True, "data": "JG12025062720250628020105002022100614ハーフェン", "filename": "sample.txt"})(),
        type("Result", (), {"return_code": 0, "has_data": False, "data": "", "filename": ""})(),
    ]
    client.read.side_effect = results

    saved_count = run_read_loop(
        client=client,
        data_spec="RACE",
        from_time="20240101000000",
        option=1,
        save_to_db=True,
        max_records=2,
        retry_wait_seconds=0.0,
        database_path=db_path,
    )

    database = KeibaDatabase(db_path=db_path)
    raw_repo = RawRecordRepository(database)
    recent = raw_repo.list_recent(limit=10)
    horse_repo = HorseRepository(database)
    horse = horse_repo.get_by_name("ハーフェン")

    assert saved_count == 1
    assert len(recent) == 1
    assert recent[0]["record_type"] == "JG"
    assert horse is not None
    assert horse["horse_name"] == "ハーフェン"


def test_horse_repository_upsert_horse_from_model_prevents_duplicate_names(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    repo = HorseRepository(database)

    from keiba_ai_agent.parser.jg_parser import Horse

    repo.upsert_horse_from_model(Horse(horse_name="サクラ", horse_id="horse-1"))
    repo.upsert_horse_from_model(Horse(horse_name="サクラ", horse_id="horse-2"))

    rows = database.connect().execute("SELECT horse_id, horse_name FROM horses WHERE horse_name = ?", ("サクラ",)).fetchall()

    assert len(rows) == 1
    assert rows[0]["horse_id"] == "horse-2"


def test_feature_models_round_trip_through_dicts() -> None:
    horse_feature = HorseFeature(horse_id="horse-1", feature_name="speed", feature_value=0.82)
    race_feature = RaceFeature(race_id="race-1", feature_name="distance", feature_value=1800)
    entry_feature = EntryFeature(race_id="race-1", horse_id="horse-1", feature_name="odds", feature_value=6.2)
    feature = Feature(feature_id="f-1", feature_name="sample", feature_value=1.0, source="test")

    assert horse_feature.to_dict()["horse_id"] == "horse-1"
    assert race_feature.to_dict()["race_id"] == "race-1"
    assert entry_feature.to_dict()["feature_name"] == "odds"
    assert Feature.from_dict(feature.to_dict()).feature_name == "sample"


def test_feature_repository_persists_features(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    repo = FeatureRepository(database)

    feature = Feature(feature_id="f-1", feature_name="speed", feature_value=0.82, source="test")
    repo.save(feature)

    saved = repo.get_by_id("f-1")
    assert saved is not None
    assert saved["feature_name"] == "speed"
    assert saved["feature_value"] == 0.82


def test_feature_builder_creates_minimal_features_and_saves_them(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    horse_repo = HorseRepository(database)
    horse_repo.upsert_horse_from_model(Horse(horse_name="サクラ", horse_id="horse-1"))

    builder = FeatureBuilder(database_path=db_path)
    saved_count = builder.save_features_for_horses()

    assert saved_count == 2
    feature_repo = FeatureRepository(database)
    saved = feature_repo.get_by_id("horse-1:horse_name_length")
    assert saved is not None
    assert saved["feature_name"] == "horse_name_length"
    assert saved["feature_value"] == 3


def test_build_features_script_runs(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    horse_repo = HorseRepository(database)
    horse_repo.upsert_horse_from_model(Horse(horse_name="テスト馬", horse_id="horse-test"))

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [sys.executable, "scripts/build_features.py", str(db_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "Saved 2 features" in result.stdout


def test_data_ingestion_service_persists_parsed_records(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    client = Mock()
    results = [
        type("Result", (), {"return_code": -3, "has_data": False, "data": "", "filename": ""})(),
        type("Result", (), {"return_code": 1, "has_data": True, "data": "JG12025062720250628020105002022100614ハーフェン", "filename": "sample.txt"})(),
        type("Result", (), {"return_code": 0, "has_data": False, "data": "", "filename": ""})(),
    ]
    client.read.side_effect = results

    service = DataIngestionService(client=client, database_path=db_path)
    saved_count = service.ingest(
        data_spec="RACE",
        from_time="20240101000000",
        option=1,
        save_to_db=True,
        max_records=2,
        retry_wait_seconds=0.0,
    )

    assert saved_count == 1
    database = KeibaDatabase(db_path=db_path)
    raw_repo = RawRecordRepository(database)
    recent = raw_repo.list_recent(limit=10)
    assert len(recent) == 1
    assert recent[0]["record_type"] == "JG"


def test_show_horses_script_runs_with_default_db_path(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    repo = HorseRepository(database)
    repo.upsert_horse_from_model(Horse(horse_name="テスト馬", horse_id="horse-test"))

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [sys.executable, "scripts/show_horses.py", str(db_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "テスト馬" in result.stdout


def test_dataset_builder_creates_one_row_per_horse_and_saves_outputs(tmp_path: Path):
    pytest.importorskip("pandas")
    from keiba_ai_agent.dataset.dataset_builder import DatasetBuilder

    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    horse_repo = HorseRepository(database)
    horse_repo.upsert_horse_from_model(Horse(horse_name="サクラ", horse_id="horse-1"))

    builder = FeatureBuilder(database_path=db_path)
    builder.save_features_for_horses()

    dataset_builder = DatasetBuilder(database_path=db_path, output_dir=tmp_path / "dataset")
    dataframe = dataset_builder.build_dataset()
    output_paths = dataset_builder.save_dataset()

    assert dataframe.shape[0] == 1
    assert "horse_name_length" in dataframe.columns
    assert dataframe.loc[0, "horse_name_length"] == 3
    assert (tmp_path / "dataset" / "dataset.csv").exists()
    assert (tmp_path / "dataset" / "dataset.parquet").exists()
    assert output_paths["csv"].exists()
    assert output_paths["parquet"].exists()


def test_build_dataset_script_runs(tmp_path: Path):
    pytest.importorskip("pandas")

    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    horse_repo = HorseRepository(database)
    horse_repo.upsert_horse_from_model(Horse(horse_name="テスト馬", horse_id="horse-test"))

    builder = FeatureBuilder(database_path=db_path)
    builder.save_features_for_horses()

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [sys.executable, "scripts/build_dataset.py", str(db_path), str(tmp_path / "dataset")],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "Saved dataset" in result.stdout


def test_show_features_script_runs_and_displays_latest_features(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO features (feature_id, feature_name, feature_value, source) VALUES (?, ?, ?, ?)",
            ("horse-1:horse_name_length", "horse_name_length", 3, "horse"),
        )
        connection.execute(
            "INSERT INTO features (feature_id, feature_name, feature_value, source) VALUES (?, ?, ?, ?)",
            ("horse-1:has_horse_id", "has_horse_id", 1, "horse"),
        )
        connection.commit()

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [sys.executable, "scripts/show_features.py", str(db_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "horse_id=horse-1" in result.stdout
    assert "feature_name=horse_name_length" in result.stdout
    assert "feature_value=3" in result.stdout


def test_show_record_types_script_reports_counts(tmp_path: Path):
    db_path = tmp_path / "keiba.db"
    database = KeibaDatabase(db_path=db_path)

    with database.connect() as connection:
        connection.execute("INSERT INTO raw_records (raw, record_type, filename, return_code) VALUES (?, ?, ?, ?)", ("JG1", "JG", "a.txt", 1))
        connection.execute("INSERT INTO raw_records (raw, record_type, filename, return_code) VALUES (?, ?, ?, ?)", ("JG2", "JG", "b.txt", 1))
        connection.execute("INSERT INTO raw_records (raw, record_type, filename, return_code) VALUES (?, ?, ?, ?)", ("RA1", "RA", "c.txt", 1))
        connection.commit()

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [sys.executable, "scripts/show_record_types.py", str(db_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "JG: 2" in result.stdout
    assert "RA: 1" in result.stdout
