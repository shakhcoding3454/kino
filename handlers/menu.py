"""
handlers/menu.py — Foydalanuvchi asosiy menyu handlerlari.

MUHIM: F.text == "..." dagi matn klaviaturadagi EXACTLY shu matn bo'lishi kerak.
Har bir handler boshida is_admin_id() tekshiruvi — admin ushbu handlerlarga
yuborilmaydi (u admin menyusini ko'radi).
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_kb import main_menu_kb, admin_menu_kb
from services.user_service import get_user
from services.referral_service import make_referral_link
from utils.filters import is_admin_id
from utils.texts import (
    vip_info_text, get_vip_kb, get_contact_kb,
    referral_info_text, hamkorlik_text, reklama_text, buyurtma_text,
)

logger = logging.getLogger(__name__)
router = Router()


# ─── 💎 VIP ───────────────────────────────────────────────────────────────────

@router.message(F.text == "💎 VIP")
async def menu_vip(message: Message) -> None:
    logger.info("💎 VIP bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        await message.answer("🛡 Admin paneli", reply_markup=admin_menu_kb())
        return
    text = await vip_info_text()
    kb   = await get_vip_kb()
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data == "show_vip")
async def cb_show_vip(call: CallbackQuery) -> None:
    text = await vip_info_text()
    kb   = await get_vip_kb()
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


# ─── 🔗 TAKLIF HAVOLAM ────────────────────────────────────────────────────────

@router.message(F.text == "🔗 Taklif havolam")
async def menu_referral(message: Message) -> None:
    logger.info("🔗 Taklif bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    db_user = await get_user(message.from_user.id)
    count   = db_user["referral_count"] if db_user else 0
    bot_me  = await message.bot.get_me()
    link    = make_referral_link(bot_me.username, message.from_user.id)
    text    = await referral_info_text(link, count)
    kb      = await get_contact_kb()
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data == "referral_info")
async def cb_referral_info(call: CallbackQuery) -> None:
    db_user = await get_user(call.from_user.id)
    count   = db_user["referral_count"] if db_user else 0
    bot_me  = await call.bot.get_me()
    link    = make_referral_link(bot_me.username, call.from_user.id)
    text    = await referral_info_text(link, count)
    kb      = await get_contact_kb()
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


# ─── 🤝 HAMKORLIK ─────────────────────────────────────────────────────────────

@router.message(F.text == "🤝 Hamkorlik")
async def menu_hamkorlik(message: Message) -> None:
    logger.info("🤝 Hamkorlik bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    text = await hamkorlik_text()
    kb   = await get_contact_kb()
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


# ─── 📢 REKLAMA ───────────────────────────────────────────────────────────────

@router.message(F.text == "📢 Reklama")
async def menu_reklama(message: Message) -> None:
    logger.info("📢 Reklama bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    text = await reklama_text()
    kb   = await get_contact_kb()
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


# ─── 📦 BUYURTMA ──────────────────────────────────────────────────────────────

@router.message(F.text == "📦 Buyurtma")
async def menu_buyurtma(message: Message) -> None:
    logger.info("📦 Buyurtma bosildi: user=%s", message.from_user.id)
    if is_admin_id(message.from_user.id):
        return
    text = await buyurtma_text()
    kb   = await get_contact_kb()
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


# ─── CALLBACK: ORQAGA ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "back_main")
async def cb_back_main(call: CallbackQuery) -> None:
    if is_admin_id(call.from_user.id):
        await call.message.answer("🛡 Admin paneli", reply_markup=admin_menu_kb())
    else:
        await call.message.answer("🏠 Asosiy menyu", reply_markup=main_menu_kb())
    await call.answer()


# ─── 🔙 FOYDALANUVCHI MENYUSI (admin paneldan qaytish) ───────────────────────

@router.message(F.text == "🔙 Foydalanuvchi menyusi")
async def switch_to_user(message: Message) -> None:
    await message.answer("🏠 Foydalanuvchi menyusi", reply_markup=main_menu_kb())
