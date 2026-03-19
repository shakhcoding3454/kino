"""utils/exceptions.py — Global error handler."""

import logging
import traceback

from aiogram import Bot
from aiogram.types import Update, ErrorEvent

from config import cfg

logger = logging.getLogger("MK.Error")


async def global_error_handler(event: ErrorEvent) -> None:
    """Barcha tutilmagan exceptionlarni loglaydi va adminga xabar beradi."""
    exc = event.exception
    upd = event.update

    # Stack trace log
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error("Unhandled exception:\n%s", tb)

    # Adminga xabar (production da)
    if cfg.ENV == "production" and cfg.ADMIN_IDS:
        try:
            bot: Bot = event.update.bot  # type: ignore
            short_tb = tb[-3000:] if len(tb) > 3000 else tb
            for admin_id in list(cfg.ADMIN_IDS)[:1]:  # faqat birinchi adminga
                await bot.send_message(
                    admin_id,
                    f"🚨 <b>Bot xatosi!</b>\n\n"
                    f"<pre>{short_tb}</pre>",
                    parse_mode="HTML",
                )
        except Exception as e:
            logger.warning("Admin ga xato yuborishda muammo: %s", e)
