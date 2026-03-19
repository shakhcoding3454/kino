"""
middlewares/rate_limit.py — Sliding window rate limiter

Har bir foydalanuvchi uchun alohida window.
Default: 3 ta xabar / 2 soniya.
Exceeded bo'lsa — xabar o'chirilmaydi, faqat warning yuboriladi.
"""

import time
import logging
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from config import cfg

logger = logging.getLogger(__name__)

_windows: dict[int, deque] = defaultdict(deque)
_warned:  set[int] = set()       # spam qilganda faqat bir marta ogohlantirish


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        uid  = event.from_user.id
        now  = time.monotonic()
        win  = cfg.RATE_LIMIT_WINDOW
        maxr = cfg.RATE_LIMIT_REQUESTS

        dq = _windows[uid]
        while dq and now - dq[0] > win:
            dq.popleft()

        if len(dq) >= maxr:
            # Faqat birinchi marta ogohlantirish
            if uid not in _warned:
                _warned.add(uid)
                try:
                    await event.answer(
                        "⏳ <b>Juda tez yuboryapsiz!</b>\n\n"
                        "Biroz kuting va qaytadan urinib ko'ring.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
            logger.debug("Rate limit: uid=%s", uid)
            return

        _warned.discard(uid)
        dq.append(now)
        return await handler(event, data)
