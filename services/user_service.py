"""services/user_service.py — User CRUD and VIP management."""

import logging
from datetime import datetime
from typing import Optional

from database.db import get_db

logger = logging.getLogger(__name__)
_now = lambda: datetime.utcnow().isoformat()


async def get_or_create_user(
    tg_id: int,
    username: Optional[str],
    full_name: str,
    referred_by: Optional[int] = None,
) -> dict:
    db = get_db()
    now = _now()

    async with db.execute(
        "SELECT * FROM users WHERE tg_id = ?", (tg_id,)
    ) as cur:
        row = await cur.fetchone()

    if row:
        await db.execute(
            "UPDATE users SET last_seen=?, username=?, full_name=? WHERE tg_id=?",
            (now, username, full_name, tg_id),
        )
        await db.commit()
        return dict(row)

    # New user
    await db.execute(
        """INSERT INTO users
           (tg_id, username, full_name, is_vip, referral_count,
            referred_by, joined_at, last_seen)
           VALUES (?,?,?,0,0,?,?,?)""",
        (tg_id, username, full_name, referred_by, now, now),
    )
    await db.commit()
    logger.info("New user registered: %s (%s)", tg_id, full_name)
    return await get_user(tg_id)


async def get_user(tg_id: int) -> Optional[dict]:
    db = get_db()
    async with db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def is_vip(tg_id: int) -> bool:
    user = await get_user(tg_id)
    return bool(user and user["is_vip"])


async def grant_vip(tg_id: int) -> None:
    db = get_db()
    await db.execute("UPDATE users SET is_vip=1 WHERE tg_id=?", (tg_id,))
    await db.commit()
    logger.info("VIP granted to user %s", tg_id)


async def revoke_vip(tg_id: int) -> None:
    db = get_db()
    await db.execute("UPDATE users SET is_vip=0 WHERE tg_id=?", (tg_id,))
    await db.commit()


async def increment_referral(referrer_id: int) -> int:
    """Increments referral count; returns new count."""
    db = get_db()
    await db.execute(
        "UPDATE users SET referral_count = referral_count + 1 WHERE tg_id=?",
        (referrer_id,),
    )
    await db.commit()
    user = await get_user(referrer_id)
    return user["referral_count"] if user else 0


async def get_all_user_ids() -> list[int]:
    db = get_db()
    async with db.execute("SELECT tg_id FROM users") as cur:
        rows = await cur.fetchall()
    return [r["tg_id"] for r in rows]


async def total_users() -> int:
    db = get_db()
    async with db.execute("SELECT COUNT(*) as c FROM users") as cur:
        row = await cur.fetchone()
    return row["c"]


async def today_new_users() -> int:
    db = get_db()
    today = datetime.utcnow().date().isoformat()
    async with db.execute(
        "SELECT COUNT(*) as c FROM users WHERE joined_at >= ?", (today,)
    ) as cur:
        row = await cur.fetchone()
    return row["c"]


async def total_vip_users() -> int:
    db = get_db()
    async with db.execute("SELECT COUNT(*) as c FROM users WHERE is_vip=1") as cur:
        row = await cur.fetchone()
    return row["c"]
