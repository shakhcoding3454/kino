"""
handlers/videos.py — 🎬 Intervyular, 🎙 Podcastlar, 🔍 Qidirish, kod handler.

MUHIM: Regex handler (kod orqali qidirish) — ENG OXIRDA bo'lishi kerak.
Bu handler barcha 3-20 belgilik matnlarni tutib oladi.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message

from services.user_service import is_vip
from services.video_service import (
    get_video_by_code, get_videos_by_category,
    increment_video_views, get_all_podcasts,
    increment_podcast_views, get_podcast_by_code,
)
from utils.filters import is_admin_id
from utils.texts import (
    video_list_text, video_caption_text, no_content_text,
    not_found_text, search_hint_text, vip_locked_text,
    get_vip_kb, get_contact_kb,
)

logger = logging.getLogger(__name__)
router = Router()


# ─── 🎬 INTERVYULAR ───────────────────────────────────────────────────────────

@router.message(F.text == "🎬 Intervyular")
async def menu_interviews(message: Message) -> None:
    logger.info("🎬 Intervyular bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    items = await get_videos_by_category("interview")
    if not items:
        await message.answer(
            await no_content_text(), parse_mode="HTML",
            reply_markup=await get_contact_kb(),
        )
        return
    text = await video_list_text(items, "video")
    await message.answer(text, parse_mode="HTML", reply_markup=await get_contact_kb())


# ─── 🎙 PODCASTLAR ────────────────────────────────────────────────────────────

@router.message(F.text == "🎙 Podcastlar")
async def menu_podcasts(message: Message) -> None:
    logger.info("🎙 Podcastlar bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    items = await get_all_podcasts()
    if not items:
        await message.answer(
            await no_content_text(), parse_mode="HTML",
            reply_markup=await get_contact_kb(),
        )
        return
    text = await video_list_text(items, "podcast")
    await message.answer(text, parse_mode="HTML", reply_markup=await get_contact_kb())


# ─── 🔍 QIDIRISH ──────────────────────────────────────────────────────────────

@router.message(F.text == "🔍 Qidirish")
async def menu_search(message: Message) -> None:
    logger.info("🔍 Qidirish bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    text = await search_hint_text()
    await message.answer(text, parse_mode="HTML", reply_markup=await get_contact_kb())


# ─── KOD ORQALI TOMOSHA (regex — ENG OXIRDA) ──────────────────────────────────

@router.message(F.text.regexp(r"^[A-Za-z0-9_\-]{3,20}$"))
async def handle_code(message: Message) -> None:
    if is_admin_id(message.from_user.id):
        return

    code     = message.text.strip().upper()
    user_vip = await is_vip(message.from_user.id)
    logger.info("Kod qidirildi: %s | user=%s", code, message.from_user.id)

    # Video tekshir
    video = await get_video_by_code(code)
    if video:
        if video["is_vip"] and not user_vip:
            await message.answer(
                await vip_locked_text(), parse_mode="HTML",
                reply_markup=await get_vip_kb(),
            )
            return
        await increment_video_views(video["id"], message.from_user.id)
        caption = await video_caption_text(
            video["title"], video["category"], video["views"] + 1
        )
        await message.answer_video(
            video=video["file_id"], caption=caption,
            parse_mode="HTML", reply_markup=await get_contact_kb(),
        )
        return

    # Podcast tekshir
    podcast = await get_podcast_by_code(code)
    if podcast:
        if podcast["is_vip"] and not user_vip:
            await message.answer(
                await vip_locked_text(), parse_mode="HTML",
                reply_markup=await get_vip_kb(),
            )
            return
        await increment_podcast_views(podcast["id"], message.from_user.id)
        caption = await video_caption_text(
            podcast["title"], "Podcast", podcast["views"] + 1
        )
        await message.answer_audio(
            audio=podcast["file_id"], caption=caption,
            parse_mode="HTML", reply_markup=await get_contact_kb(),
        )
        return

    await message.answer(
        await not_found_text(), parse_mode="HTML",
        reply_markup=await get_contact_kb(),
    )
