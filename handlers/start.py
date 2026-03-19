"""
handlers/start.py

/start  — ro'yxatdan o'tish + referral
/admin  — parol orqali panel
/help   — yordam
parol   — klub2026
"""

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import cfg
from keyboards.main_kb import main_menu_kb, admin_menu_kb
from services.user_service import get_or_create_user, get_user
from services.referral_service import parse_referral_payload, process_referral
from utils.filters import is_admin_id, add_session_admin
from utils.texts import welcome_text, welcome_referred_text

logger = logging.getLogger("MK.Start")
router = Router()


class AdminAuth(StatesGroup):
    waiting_password = State()


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.clear()
    user     = message.from_user
    payload  = command.args or ""
    ref_id   = parse_referral_payload(payload)

    await get_or_create_user(
        tg_id=user.id,
        username=user.username,
        full_name=user.full_name,
        referred_by=ref_id,
    )

    if is_admin_id(user.id):
        await _show_admin_panel(message)
        return

    if ref_id and ref_id != user.id:
        referrer = await get_user(ref_id)
        if referrer:
            await process_referral(
                bot=message.bot,
                new_user_tg_id=user.id,
                referrer_tg_id=ref_id,
            )
        text = await welcome_referred_text(user.first_name or "Do'st")
    else:
        text = await welcome_text(user.first_name or "Do'st")

    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())


# ─── /help ────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if is_admin_id(message.from_user.id):
        await message.answer(
            "🛡 <b>Admin buyruqlari:</b>\n\n"
            "/admin — Admin panelni ochish\n"
            "/help  — Yordam\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Panel ichidan:\n"
            "🎬 Video / 🎙 Podcast / 🔥 Short qo'shish\n"
            "📊 Statistika ko'rish\n"
            "📢 Broadcast yuborish\n"
            "👑 VIP berish / olish\n"
            "⚙️ Admin username sozlash",
            parse_mode="HTML",
        )
        return

    from utils.texts import _admin_contact
    contact = await _admin_contact()
    await message.answer(
        "ℹ️ <b>Yordam — Milliarderlar Klubi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎬 <b>Intervyular</b> — Milliardyorlar suhbatlari\n"
        "🎙 <b>Podcastlar</b>  — Audio darslar\n"
        "🔥 <b>Shorts</b>      — Qisqa motivatsiya\n"
        "💎 <b>VIP</b>         — Premium a'zolik\n"
        "🔍 <b>Qidirish</b>    — Kod orqali video topish\n"
        "🔗 <b>Taklif</b>      — Do'st taklif → bepul VIP\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{contact}",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ─── /admin ───────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    if is_admin_id(message.from_user.id):
        await state.clear()
        await _show_admin_panel(message)
        return

    await state.set_state(AdminAuth.waiting_password)
    await message.answer(
        "🔐 <b>Admin paneli</b>\n\n"
        "Kirish uchun parolni yuboring:\n"
        "<i>(Xabar yuborilgandan so'ng o'chiriladi)</i>",
        parse_mode="HTML",
    )


# ─── Parol tekshirish ─────────────────────────────────────────────────────────

@router.message(AdminAuth.waiting_password)
async def check_password(message: Message, state: FSMContext) -> None:
    entered = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass

    if entered == cfg.ADMIN_PASSWORD:
        add_session_admin(message.from_user.id)
        await state.clear()
        logger.info("✅ Admin kirdi (parol): uid=%s", message.from_user.id)
        await _show_admin_panel(message)
    else:
        await state.clear()
        logger.warning("❌ Noto'g'ri parol: uid=%s", message.from_user.id)
        await message.answer(
            "❌ <b>Noto'g'ri parol!</b>\n\n"
            "Qaytadan urinish: /admin",
            parse_mode="HTML",
        )


# ─── Admin panel ──────────────────────────────────────────────────────────────

async def _show_admin_panel(message: Message) -> None:
    from services.settings_service import get_admin_username
    name    = message.from_user.first_name or "Admin"
    uname   = await get_admin_username()
    u_badge = f"✅ @{uname}" if uname else "⚠️ O'rnatilmagan"

    await message.answer(
        f"🛡 <b>Xush kelibsiz, {name}!</b>\n\n"
        "┌─────────────────────────────┐\n"
        "│  ⚙️  ADMIN BOSHQARUV PANELI  │\n"
        "│    Milliarderlar Klubi Bot  │\n"
        "└─────────────────────────────┘\n\n"
        f"📌 Murojaat username: <b>{u_badge}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📹 <b>KONTENT</b>\n"
        "  🎬 Video qo'shish\n"
        "  🎙 Podcast qo'shish\n"
        "  🔥 Short qo'shish\n"
        "  🗑 Video o'chirish\n\n"
        "👥 <b>FOYDALANUVCHILAR</b>\n"
        "  👑 VIP berish\n"
        "  ❌ VIP olish\n\n"
        "📊 <b>BOSHQARUV</b>\n"
        "  📊 Statistika\n"
        "  📢 Broadcast\n"
        "  ⚙️ Admin username\n"
        "━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )
