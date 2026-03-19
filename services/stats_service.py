"""services/stats_service.py — Aggregated statistics for admin panel."""

from database.db import get_db
from services.user_service import total_users, today_new_users, total_vip_users
from services.video_service import get_most_popular_video


async def get_full_stats() -> dict:
    db = get_db()

    async with db.execute("SELECT COUNT(*) as c FROM videos") as cur:
        total_videos = (await cur.fetchone())["c"]

    async with db.execute("SELECT COUNT(*) as c FROM podcasts") as cur:
        total_podcasts = (await cur.fetchone())["c"]

    async with db.execute("SELECT COUNT(*) as c FROM shorts") as cur:
        total_shorts = (await cur.fetchone())["c"]

    async with db.execute("SELECT SUM(views) as s FROM videos") as cur:
        row = await cur.fetchone()
        total_views = row["s"] or 0

    top_video = await get_most_popular_video()

    return {
        "total_users":    await total_users(),
        "today_users":    await today_new_users(),
        "vip_users":      await total_vip_users(),
        "total_videos":   total_videos,
        "total_podcasts": total_podcasts,
        "total_shorts":   total_shorts,
        "total_views":    total_views,
        "top_video":      top_video,
    }
