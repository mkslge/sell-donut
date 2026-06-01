from __future__ import annotations

SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sellers (
    id TEXT PRIMARY KEY,
    seller_username TEXT NOT NULL,
    normalized_username TEXT NOT NULL UNIQUE,
    minecraft_uuid TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ratings (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    seller_username TEXT NOT NULL,
    normalized_username TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('LEGIT', 'SCAMMER', 'MIXED')),
    item_type TEXT NOT NULL,
    item_name TEXT,
    quantity INTEGER,
    price REAL,
    currency TEXT,
    description TEXT,
    evidence_url TEXT,
    reporter_username TEXT,
    submitterFingerprint TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ratings_normalized_username
ON ratings(normalized_username);

CREATE INDEX IF NOT EXISTS idx_ratings_created_at
ON ratings(created_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sellers_minecraft_uuid
ON sellers(minecraft_uuid)
WHERE minecraft_uuid IS NOT NULL;

CREATE TABLE IF NOT EXISTS logging (
    id INTEGER NOT NULL PRIMARY KEY CHECK (id = 1),
    visit_count INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO logging (id, visit_count)
VALUES (1, 0);
"""


SQLITE_RATINGS_MIGRATION_SQL = """
ALTER TABLE ratings RENAME TO ratings_old;

CREATE TABLE ratings (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    seller_username TEXT NOT NULL,
    normalized_username TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('LEGIT', 'SCAMMER', 'MIXED')),
    item_type TEXT NOT NULL,
    item_name TEXT,
    quantity INTEGER,
    price REAL,
    currency TEXT,
    description TEXT,
    evidence_url TEXT,
    reporter_username TEXT,
    submitterFingerprint TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
);
"""


SQLITE_RATINGS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_ratings_normalized_username
ON ratings(normalized_username);

CREATE INDEX IF NOT EXISTS idx_ratings_created_at
ON ratings(created_at);
"""


SQLITE_LOGGING_SQL = """
CREATE TABLE IF NOT EXISTS logging (
    id INTEGER NOT NULL PRIMARY KEY CHECK (id = 1),
    visit_count INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO logging (id, visit_count)
VALUES (1, 0);
"""
