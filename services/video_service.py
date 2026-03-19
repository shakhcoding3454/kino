"""services/video_service.py — Video and Podcast CRUD."""

import logging
from datetime import datetime
from typing import Optional

from database.db import get_db

logger = logging.getLogger(__name__)
_now = lambda: datetime.utcnow().isoformat()


# ─── VIDEOS ──────────────────────────────────────────────────────────────────

async def code_exists(code: str, table: str = "videos") -> bool:
    db = get_db()
    async with db.execute(
        f"SELECT 1 FROM {table} WHERE code=?", (code,)
    ) as cur:
        return await cur.fetchone() is not None


async def add_video(
    code: str,
    title: str,
    file_id: str,
    category: str,
    is_vip: bool,
    added_by: int,
) -> dict:
    db = get_db()
    await db.execute(
        """INSERT INTO videos (code, title, file_id, category, is_vip, added_by, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (code, title, file_id, category, int(is_vip), added_by, _now()),
    )
    await db.commit()
    return await get_video_by_code(code)


async def get_video_by_code(code: str) -> Optional[dict]:
    db = get_db()
    async with db.execute("SELECT * FROM videos WHERE code=?", (code,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def increment_video_views(video_id: int, user_tg_id: int) -> None:
    db = get_db()
    await db.execute(
        "UPDATE videos SET views = views + 1 WHERE id=?", (video_id,)
    )
    await db.execute(
        "INSERT INTO views_log (user_tg_id, content_type, content_id, viewed_at) VALUES (?,?,?,?)",
        (user_tg_id, "video", video_id, _now()),
    )
    await db.commit()


async def get_videos_by_category(category: str, limit: int = 20) -> list[dict]:
    db = get_db()
    async with db.execute(
        "SELECT * FROM videos WHERE category=? ORDER BY created_at DESC LIMIT ?",
        (category, limit),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_most_popular_video() -> Optional[dict]:
    db = get_db()
    async with db.execute(
        "SELECT * FROM videos ORDER BY views DESC LIMIT 1"
    ) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def delete_video(code: str) -> bool:
    db = get_db()
    async with db.execute("SELECT id FROM videos WHERE code=?", (code,)) as cur:
        row = await cur.fetchone()
    if not row:
        return False
    await db.execute("DELETE FROM videos WHERE code=?", (code,))
    await db.commit()
    return True


# ─── PODCASTS ────────────────────────────────────────────────────────────────

async def add_podcast(
    code: str,
    title: str,
    file_id: str,
    is_vip: bool,
    added_by: int,
) -> dict:
    db = get_db()
    await db.execute(
        """INSERT INTO podcasts (code, title, file_id, is_vip, added_by, created_at)
           VALUES (?,?,?,?,?,?)""",
        (code, title, file_id, int(is_vip), added_by, _now()),
    )
    await db.commit()
    return await get_podcast_by_code(code)


async def get_podcast_by_code(code: str) -> Optional[dict]:
    db = get_db()
    async with db.execute("SELECT * FROM podcasts WHERE code=?", (code,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def get_all_podcasts(limit: int = 20) -> list[dict]:
    db = get_db()
    async with db.execute(
        "SELECT * FROM podcasts ORDER BY created_at DESC LIMIT ?", (limit,)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def increment_podcast_views(podcast_id: int, user_tg_id: int) -> None:
    db = get_db()
    await db.execute(
        "UPDATE podcasts SET views = views + 1 WHERE id=?", (podcast_id,)
    )
    await db.execute(
        "INSERT INTO views_log (user_tg_id, content_type, content_id, viewed_at) VALUES (?,?,?,?)",
        (user_tg_id, "podcast", podcast_id, _now()),
    )
    await db.commit()
