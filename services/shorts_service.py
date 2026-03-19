"""services/shorts_service.py — Shorts CRUD."""

from datetime import datetime
from typing import Optional
from database.db import get_db

_now = lambda: datetime.utcnow().isoformat()


async def add_short(title: str, text: str) -> dict:
    db = get_db()
    await db.execute(
        "INSERT INTO shorts (title, text, created_at) VALUES (?,?,?)",
        (title, text, _now()),
    )
    await db.commit()
    async with db.execute(
        "SELECT * FROM shorts ORDER BY id DESC LIMIT 1"
    ) as cur:
        row = await cur.fetchone()
    return dict(row)


async def get_short_by_id(short_id: int) -> Optional[dict]:
    db = get_db()
    async with db.execute("SELECT * FROM shorts WHERE id=?", (short_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def get_next_short(current_id: int) -> Optional[dict]:
    """Returns the next short after current_id, wraps to first."""
    db = get_db()
    async with db.execute(
        "SELECT * FROM shorts WHERE id > ? ORDER BY id ASC LIMIT 1", (current_id,)
    ) as cur:
        row = await cur.fetchone()
    if row:
        return dict(row)
    # Wrap around to first
    async with db.execute("SELECT * FROM shorts ORDER BY id ASC LIMIT 1") as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def get_first_short() -> Optional[dict]:
    db = get_db()
    async with db.execute("SELECT * FROM shorts ORDER BY id ASC LIMIT 1") as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def total_shorts() -> int:
    db = get_db()
    async with db.execute("SELECT COUNT(*) as c FROM shorts") as cur:
        row = await cur.fetchone()
    return row["c"]


async def delete_short(short_id: int) -> bool:
    db = get_db()
    async with db.execute("SELECT id FROM shorts WHERE id=?", (short_id,)) as cur:
        row = await cur.fetchone()
    if not row:
        return False
    await db.execute("DELETE FROM shorts WHERE id=?", (short_id,))
    await db.commit()
    return True
