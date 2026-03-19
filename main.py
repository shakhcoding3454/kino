"""
main.py — Milliarderlar Klubi Bot  (Railway Production)
─────────────────────────────────────────────────────────
Stack: Aiogram 3.13 · aiosqlite · aiohttp · Python 3.11
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime

from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from config import cfg
from database.db import init_db, close_db, get_db
from middlewares.rate_limit import RateLimitMiddleware
from middlewares.logging_mw import LoggingMiddleware
from utils.exceptions import global_error_handler
from handlers import start, menu, videos, shorts, marketing, admin

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
for noisy in ("aiogram", "aiosqlite", "aiohttp"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger("MK.Main")

# ─── HEALTH SERVER ────────────────────────────────────────────────────────────

_start_time = datetime.utcnow()


async def handle_health(_req: web.Request) -> web.Response:
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    try:
        db    = get_db()
        async with db.execute("SELECT COUNT(*) as c FROM users") as cur:
            row = await cur.fetchone()
        users = row["c"] if row else 0
        db_ok = True
    except Exception:
        users, db_ok = 0, False

    return web.Response(
        text=json.dumps({
            "status":   "ok" if db_ok else "degraded",
            "uptime_s": round(uptime),
            "env":      cfg.ENV,
            "db":       "ok" if db_ok else "error",
            "users":    users,
        }),
        content_type="application/json",
        status=200 if db_ok else 503,
    )


async def handle_root(_req: web.Request) -> web.Response:
    return web.Response(text="Milliarderlar Klubi Bot — online")


async def start_health_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/",       handle_root)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", cfg.PORT).start()
    logger.info("🌐 Health: http://0.0.0.0:%s/health", cfg.PORT)
    return runner


# ─── FALLBACK ─────────────────────────────────────────────────────────────────

fallback_router = Router()

@fallback_router.message()
async def unhandled(message: Message) -> None:
    uid  = message.from_user.id if message.from_user else "?"
    text = message.text or f"[{message.content_type}]"
    logger.warning("UNHANDLED uid=%-10s %r", uid, text[:80])


# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    logger.info("=" * 55)
    logger.info("  MILLIARDERLAR KLUBI BOT  |  env=%s", cfg.ENV)
    logger.info("=" * 55)
    logger.info("DB   : %s", cfg.DB_PATH)
    logger.info("Port : %s", cfg.PORT)

    # 1. DB
    await init_db()

    # 2. Health server (Railway uchun majburiy)
    runner = await start_health_server()

    # 3. Bot
    bot = Bot(
        token=cfg.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # 4. Dispatcher
    dp = Dispatcher(storage=MemoryStorage())

    # 5. Middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware())

    # 6. Error handler
    dp.errors.register(global_error_handler)

    # 7. Routers — TARTIB O'ZGARTIRISH MUMKIN EMAS
    dp.include_router(start.router)      # /start /admin /help + parol FSM
    dp.include_router(admin.router)      # admin tugmalari (IsAdmin per-handler)
    dp.include_router(admin.fsm_router)  # admin FSM states
    dp.include_router(menu.router)       # 💎 🤝 📢 📦 🔗
    dp.include_router(shorts.router)     # 🔥
    dp.include_router(marketing.router)  # rezerv
    dp.include_router(videos.router)     # 🎬 🎙 🔍 + kod regex (oxirda!)
    dp.include_router(fallback_router)   # log unhandled

    # 8. Lifecycle hooks
    async def on_startup(b: Bot) -> None:
        logger.info("🤖 BOT JONLI — polling boshlandi")
        me = await b.get_me()
        logger.info("🤖 @%s (id=%s)", me.username, me.id)
        for uid in cfg.ADMIN_IDS:
            try:
                await b.send_message(
                    uid,
                    f"🚀 <b>Bot ishga tushdi!</b>\n\n"
                    f"🤖 @{me.username}\n"
                    f"🌍 Muhit: <b>{cfg.ENV}</b>\n"
                    f"🗄 DB: <code>{cfg.DB_PATH}</code>",
                )
            except Exception:
                pass

    async def on_shutdown(b: Bot) -> None:
        logger.info("⏹  Shutdown...")
        for uid in cfg.ADMIN_IDS:
            try:
                await b.send_message(uid, "⏹ <b>Bot to'xtatildi.</b>")
            except Exception:
                pass

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 9. Graceful shutdown
    stop_event = asyncio.Event()

    def _sig(*_):
        logger.info("🛑 Signal — to'xtamoqda...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _sig)
        except NotImplementedError:
            pass

    # 10. Polling
    polling = asyncio.create_task(
        dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    )

    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        polling.cancel()
        try:
            await polling
        except asyncio.CancelledError:
            pass
        await bot.session.close()
        await runner.cleanup()
        await close_db()
        logger.info("✅ To'liq to'xtatildi")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
