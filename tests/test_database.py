from pathlib import Path

from keiba_ai_agent.database import (
    KeibaDatabase,
    RaceRepository,
    HorseRepository,
    EntryRepository,
    RawRecordRepository,
)


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
