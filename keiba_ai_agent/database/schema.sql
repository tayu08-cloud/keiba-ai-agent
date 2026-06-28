CREATE TABLE IF NOT EXISTS races (
    race_id TEXT PRIMARY KEY,
    race_date TEXT NOT NULL,
    racecourse TEXT NOT NULL,
    race_number INTEGER NOT NULL,
    race_name TEXT NOT NULL,
    distance INTEGER,
    surface TEXT
);

CREATE TABLE IF NOT EXISTS horses (
    horse_id TEXT PRIMARY KEY,
    horse_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    race_id TEXT NOT NULL,
    horse_id TEXT NOT NULL,
    frame_number INTEGER,
    horse_number INTEGER,
    jockey TEXT,
    trainer TEXT,
    odds REAL,
    score INTEGER,
    PRIMARY KEY (race_id, horse_id),
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (horse_id) REFERENCES horses(horse_id)
);

CREATE TABLE IF NOT EXISTS raw_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw TEXT NOT NULL,
    record_type TEXT NOT NULL,
    filename TEXT,
    return_code INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS features (
    feature_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    feature_value REAL,
    source TEXT
);
