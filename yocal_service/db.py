"""SQLite cache of music (and later other fetched) assets, with the source each came from."""
from __future__ import annotations

import os
import sqlite3

DEFAULT = os.path.join("db", "yocal", "YOCal_Music.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS music_asset (
  id INTEGER PRIMARY KEY,
  url TEXT NOT NULL UNIQUE,         -- where it was fetched from
  source TEXT NOT NULL,             -- 'anca' | 'dcs'
  title TEXT NOT NULL,              -- hymn title as shown on the stand
  label TEXT NOT NULL DEFAULT '',   -- composer / arrangement
  form TEXT NOT NULL DEFAULT '',    -- 'score' | 'byzantine' | 'western' | 'audio'
  mime TEXT,
  content BLOB,                     -- NULL until fetched
  sha256 TEXT,
  size INTEGER,
  fetched_at TEXT,
  error TEXT
);
CREATE TABLE IF NOT EXISTS music_page (     -- rendered PNG pages of a PDF asset
  asset_id INTEGER NOT NULL REFERENCES music_asset(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  png BLOB NOT NULL,
  PRIMARY KEY (asset_id, page)
);
CREATE TABLE IF NOT EXISTS music_ref (      -- which assets belong to which slot of which service
  service TEXT NOT NULL,
  date TEXT NOT NULL,
  slot_key TEXT NOT NULL,
  title TEXT NOT NULL,
  asset_id INTEGER NOT NULL REFERENCES music_asset(id) ON DELETE CASCADE,
  rank INTEGER NOT NULL,
  PRIMARY KEY (service, date, slot_key, asset_id)
);
CREATE INDEX IF NOT EXISTS music_ref_slot ON music_ref(service, slot_key, date);
"""


def path() -> str:
    return os.environ.get("YOCAL_MUSIC_DB", DEFAULT)


def connect(db_path: str | None = None) -> sqlite3.Connection:
    p = db_path or path()
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    return con
