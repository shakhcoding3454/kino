"""services/referral_service.py — Referral link va mukofot tizimi."""

import logging
from aiogram import Bot
from config import cfg
from services.user_service import get_user, increment_referral, grant_vip

logger = logging.getLogger(__name__)


def make_referral_link(bot_username: str, user_tg_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_tg_id}"


def parse_referral_payload(payload: str) -> int | None:
    if payload and payload.startswith("ref_"):
        try:
            return int(payload[4:])
        except ValueError:
            pass
    return None


async def process_referral(bot: Bot, new_user_tg_id: int, referrer_tg_id: int) -> None:
    if new_user_tg_id == referrer_tg_id:
        return

    referrer = await get_user(referrer_tg_id)
    if not referrer:
        return

    new_count = await increment_referral(referrer_tg_id)
    t = cfg.REFERRAL_VIP_THRESHOLD
    remaining = max(0, t - new_count)

    logger.info("Referral: %s -> %s | count=%s", referrer_tg_id, new_user_tg_id, new_count)

    # Referrer ga xabar
    try:
        if new_count >= t:
            msg = (
                "🎉 <b>Yangi taklif qabul qilindi!</b>\n\n"
                f"📊 Takliflar: <b>{new_count}/{t}</b>\n\n"
                "✅ <b>VIP olish uchun yetarli! Pastdagi xabarni kuting.</b>"
            )
        else:
            bar = "🟡" * new_count + "⚫️" * remaining
            msg = (
                "🎉 <b>Yangi taklif qabul qilindi!</b>\n\n"
                f"📊 Progress: {bar}\n"
                f"<b>{new_count}/{t}</b>\n\n"
                f"⏳ Yana <b>{remaining} ta</b> taklif qiling → VIP bepul!"
            )
        await bot.send_message(referrer_tg_id, msg, parse_mode="HTML")
    except Exception as e:
        logger.warning("Notify referrer fail %s: %s", referrer_tg_id, e)

    # VIP mukofot
    if new_count >= t and not referrer["is_vip"]:
        await grant_vip(referrer_tg_id)
        try:
            from services.settings_service import get_admin_username
            username = await get_admin_username()
            contact  = f"@{username}" if username else "admin"
            await bot.send_message(
                referrer_tg_id,
                "👑 <b>TABRIKLAYMIZ! VIP A'ZOLIK BERILDI!</b>\n\n"
                f"Siz <b>{t} ta do'stingizni</b> taklif qildingiz\n"
                "va <b>VIP maqomiga</b> erishdingiz!\n\n"
                "💎 Endi barcha eksklyuziv kontentlarga\n"
                "to'liq kirish imkoniyatingiz bor.\n\n"
                f"📩 Savollar uchun: {contact}",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("VIP award msg fail %s: %s", referrer_tg_id, e)
