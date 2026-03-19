"""
services/settings_service.py

DB da saqlangan dinamik sozlamalar.
Admin o'z username ini qo'yishi mumkin — bu barcha xabarlarda ishlatiladi.
"""

from database.db import get_db


async def get_setting(key: str, default: str = "") -> str:
    db = get_db()
    async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
        row = await cur.fetchone()
    return row["value"] if row else default


async def set_setting(key: str, value: str) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    await db.commit()


async def get_admin_username() -> str:
    """
    Admin username ni qaytaradi.
    Agar DBda yo'q bo'lsa — config dagi default ishlatiladi.
    Agar config ham bo'sh — None qaytaradi (admin yo'q degan belgi).
    """
    from config import cfg
    db_val = await get_setting("admin_username", "")
    if db_val:
        return db_val
    if cfg.ADMIN_USERNAME:
        return cfg.ADMIN_USERNAME
    return ""
