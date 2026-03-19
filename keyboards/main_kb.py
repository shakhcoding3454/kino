"""keyboards/main_kb.py — Barcha klaviaturalar."""

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


def main_menu_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for btn in [
        "🎬 Intervyular",     "🎙 Podcastlar",
        "🔥 Shorts",           "💎 VIP",
        "📦 Buyurtma",         "🤝 Hamkorlik",
        "📢 Reklama",          "🔍 Qidirish",
        "🔗 Taklif havolam",
    ]:
        b.button(text=btn)
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)


def admin_menu_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for btn in [
        "🎬 Video qo'shish",     "🎙 Podcast qo'shish",
        "🔥 Short qo'shish",     "🗑 Video o'chirish",
        "📊 Statistika",          "📢 Broadcast",
        "👑 VIP berish",          "❌ VIP olish",
        "⚙️ Admin username",      "🔙 Foydalanuvchi menyusi",
    ]:
        b.button(text=btn)
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text="❌ Bekor qilish")
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)


def shorts_nav_kb(current_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="▶️ Keyingisi", callback_data=f"short_next:{current_id}")
    b.adjust(1)
    return b.as_markup()
