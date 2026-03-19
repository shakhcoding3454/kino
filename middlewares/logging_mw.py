"""
middlewares/logging_mw.py — Request logging middleware

Har bir xabarni loglaydi: kim, nima yozdi, qancha vaqt ketdi.
Production da INFO, development da DEBUG level.
"""

import time
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger("MK.Access")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.monotonic()

        if isinstance(event, Message) and event.from_user:
            uid  = event.from_user.id
            name = event.from_user.full_name
            text = event.text or f"[{event.content_type}]"
            logger.info("MSG uid=%-12s %-20s | %r", uid, name[:20], text[:60])

        elif isinstance(event, CallbackQuery) and event.from_user:
            uid  = event.from_user.id
            data_str = event.data or ""
            logger.info("CBQ uid=%-12s data=%r", uid, data_str[:40])

        result = await handler(event, data)
        elapsed = (time.monotonic() - start) * 1000
        logger.debug("Handler %.1fms", elapsed)
        return result
