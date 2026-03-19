"""services/broadcast_service.py — Send a message to all users."""

import asyncio
import logging
from typing import Union

from aiogram import Bot
from aiogram.types import Message

from services.user_service import get_all_user_ids

logger = logging.getLogger(__name__)


async def broadcast(bot: Bot, message: Message) -> tuple[int, int]:
    """
    Forwards `message` to every user.
    Returns (success_count, fail_count).
    """
    user_ids = await get_all_user_ids()
    success = fail = 0

    for uid in user_ids:
        try:
            await message.copy_to(uid)
            success += 1
        except Exception as e:
            logger.debug("Broadcast fail uid=%s: %s", uid, e)
            fail += 1
        await asyncio.sleep(0.04)   # ~25 msg/s — stay under Telegram limits

    logger.info("Broadcast done: ✅ %s  ❌ %s", success, fail)
    return success, fail
