"""handlers/shorts.py — 🔥 Shorts."""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_kb import shorts_nav_kb
from services.shorts_service import get_first_short, get_next_short, total_shorts
from utils.filters import is_admin_id
from utils.texts import short_card_text, no_shorts_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "🔥 Shorts")
async def menu_shorts(message: Message) -> None:
    logger.info("🔥 Shorts bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    short = await get_first_short()
    if not short:
        await message.answer(await no_shorts_text(), parse_mode="HTML")
        return
    total = await total_shorts()
    text  = await short_card_text(short["title"], short["text"], 1, total)
    await message.answer(text, parse_mode="HTML", reply_markup=shorts_nav_kb(short["id"]))


@router.callback_query(F.data.startswith("short_next:"))
async def cb_short_next(call: CallbackQuery) -> None:
    current_id = int(call.data.split(":")[1])
    short = await get_next_short(current_id)
    if not short:
        short = await get_first_short()
        if not short:
            await call.answer("Shorts bo'sh!", show_alert=True)
            return
    total = await total_shorts()
    text  = await short_card_text(short["title"], short["text"], short["id"], total)
    await call.message.edit_text(
        text, parse_mode="HTML", reply_markup=shorts_nav_kb(short["id"])
    )
    await call.answer()
