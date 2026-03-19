"""
database/db.py — Async SQLite (aiosqlite)

Railway muhim eslatma:
  - Har restart da /data papkasi saqlanadi (persistent volume)
  - DB_PATH=/data/bot.db bo'lishi kerak Railway da

WAL mode — concurrent read/write uchun optimal.
"""

import logging
import os
import aiosqlite

from config import cfg

logger = logging.getLogger(__name__)

_db: aiosqlite.Connection | None = None


async def init_db() -> None:
    """Startup da bir marta chaqiriladi."""
    global _db

    db_dir = os.path.dirname(cfg.DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        logger.info("DB papkasi: %s", db_dir)

    _db = await aiosqlite.connect(cfg.DB_PATH, timeout=30)
    _db.row_factory = aiosqlite.Row

    # Performance va ishonchlilik sozlamalari
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA synchronous=NORMAL")
    await _db.execute("PRAGMA foreign_keys=ON")
    await _db.execute("PRAGMA cache_size=-32000")   # 32MB cache
    await _db.execute("PRAGMA temp_store=MEMORY")

    await _create_tables()
    await _db.commit()
    logger.info("✅ Database tayyor: %s", cfg.DB_PATH)


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None
        logger.info("✅ Database yopildi")


def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database ishga tushmagan. init_db() ni chaqiring.")
    return _db


async def _create_tables() -> None:
    db = get_db()
    await db.executescript("""
    -- Foydalanuvchilar
    CREATE TABLE IF NOT EXISTS users (
        id             INTEGER PRIMARY KEY,
        tg_id          INTEGER UNIQUE NOT NULL,
        username       TEXT,
        full_name      TEXT NOT NULL DEFAULT '',
        is_vip         INTEGER NOT NULL DEFAULT 0,
        referral_count INTEGER NOT NULL DEFAULT 0,
        referred_by    INTEGER,
        joined_at      TEXT NOT NULL,
        last_seen      TEXT NOT NULL
    );

    -- Sozlamalar (key-value store)
    CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    -- Videolar
    CREATE TABLE IF NOT EXISTS videos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        code       TEXT UNIQUE NOT NULL COLLATE NOCASE,
        title      TEXT NOT NULL,
        file_id    TEXT NOT NULL,
        category   TEXT NOT NULL DEFAULT 'interview',
        views      INTEGER NOT NULL DEFAULT 0,
        is_vip     INTEGER NOT NULL DEFAULT 0,
        added_by   INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );

    -- Podcastlar
    CREATE TABLE IF NOT EXISTS podcasts (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        code       TEXT UNIQUE NOT NULL COLLATE NOCASE,
        title      TEXT NOT NULL,
        file_id    TEXT NOT NULL,
        views      INTEGER NOT NULL DEFAULT 0,
        is_vip     INTEGER NOT NULL DEFAULT 0,
        added_by   INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );

    -- Shorts
    CREATE TABLE IF NOT EXISTS shorts (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        text       TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- Ko'rishlar logi (statistika uchun)
    CREATE TABLE IF NOT EXISTS views_log (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_tg_id   INTEGER NOT NULL,
        content_type TEXT NOT NULL CHECK(content_type IN ('video','podcast')),
        content_id   INTEGER NOT NULL,
        viewed_at    TEXT NOT NULL
    );

    -- Indekslar
    CREATE INDEX IF NOT EXISTS idx_users_tg_id  ON users(tg_id);
    CREATE INDEX IF NOT EXISTS idx_users_vip     ON users(is_vip);
    CREATE INDEX IF NOT EXISTS idx_users_joined  ON users(joined_at);
    CREATE INDEX IF NOT EXISTS idx_videos_code   ON videos(code);
    CREATE INDEX IF NOT EXISTS idx_videos_cat    ON videos(category);
    CREATE INDEX IF NOT EXISTS idx_videos_views  ON videos(views DESC);
    CREATE INDEX IF NOT EXISTS idx_podcasts_code ON podcasts(code);
    CREATE INDEX IF NOT EXISTS idx_views_content ON views_log(content_type, content_id);
    """)
