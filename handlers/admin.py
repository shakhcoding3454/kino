"""
handlers/admin.py — Admin panel (Aiogram 3)

MUHIM: router.message.filter(IsAdmin()) ISHLATILMAYDI.
Sabab: Bu filter barcha xabarlarni tutib qoladi va oddiy
foydalanuvchi xabarlari menu.router, videos.router ga yetmaydi.

Yechim: IsAdmin() faqat har bir @router.message(...) da alohida qo'llanadi.
FSM state handlerlari is_admin_id() tekshiruvi bilan himoyalangan.
"""

import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import cfg
from keyboards.main_kb import admin_menu_kb, cancel_kb, main_menu_kb
from services.video_service import add_video, add_podcast, code_exists, delete_video
from services.shorts_service import add_short
from services.stats_service import get_full_stats
from services.broadcast_service import broadcast
from services.user_service import grant_vip, revoke_vip, get_user
from services.settings_service import set_setting, get_admin_username
from utils.filters import IsAdmin, is_admin_id
from utils.texts import stats_text

logger = logging.getLogger(__name__)

# ─── ROUTER SETUP ─────────────────────────────────────────────────────────────
# router     — admin tugma entry-pointlari (har birida IsAdmin filter)
# fsm_router — FSM state handlerlari (is_admin_id() bilan himoyalangan)

router     = Router()   # ← router.message.filter(IsAdmin()) YO'Q!
fsm_router = Router()


# ─── STATES ───────────────────────────────────────────────────────────────────

class AddVideo(StatesGroup):
    waiting_file     = State()
    waiting_title    = State()
    waiting_code     = State()
    waiting_category = State()
    waiting_vip      = State()


class AddPodcast(StatesGroup):
    waiting_file  = State()
    waiting_title = State()
    waiting_code  = State()
    waiting_vip   = State()


class AddShort(StatesGroup):
    waiting_title = State()
    waiting_text  = State()


class BroadcastStates(StatesGroup):
    waiting_message = State()
    waiting_confirm = State()


class GrantVIPState(StatesGroup):
    waiting_user_id = State()


class RevokeVIPState(StatesGroup):
    waiting_user_id = State()


class DeleteVideoState(StatesGroup):
    waiting_code = State()


class SetUsernameState(StatesGroup):
    waiting_username = State()


# ─── BEKOR QILISH (FSM da ishlaydi) ──────────────────────────────────────────

@fsm_router.message(F.text == "❌ Bekor qilish")
async def cancel_any(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id):
        return
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=admin_menu_kb())


# ════════════════════════════════════════════════════════════════════════════
# 🎬 VIDEO QO'SHISH
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "🎬 Video qo'shish")
async def start_add_video(message: Message, state: FSMContext) -> None:
    await state.set_state(AddVideo.waiting_file)
    await message.answer(
        "📹 <b>Yangi video qo'shish</b>\n\n"
        "1-qadam: Video faylini yuboring 👇",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(AddVideo.waiting_file, F.video)
async def av_got_file(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.update_data(file_id=message.video.file_id)
    await state.set_state(AddVideo.waiting_title)
    await message.answer(
        "2-qadam: ✏️ Video <b>nomini</b> kiriting:\n"
        "<i>Masalan: Elon Musk — SpaceX Sirlari</i>",
        parse_mode="HTML",
    )


@fsm_router.message(AddVideo.waiting_file)
async def av_bad_file(message: Message) -> None:
    if not is_admin_id(message.from_user.id): return
    await message.answer("⚠️ Iltimos, video fayl yuboring.")


@fsm_router.message(AddVideo.waiting_title)
async def av_got_title(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddVideo.waiting_code)
    await message.answer(
        "3-qadam: 🔑 <b>Noyob kod</b> kiriting\n\n"
        "• Faqat lotin harflari va raqamlar\n"
        "• Masalan: <code>ELON001</code>\n"
        "• ⚠️ Kod takrorlanmasligi kerak",
        parse_mode="HTML",
    )


@fsm_router.message(AddVideo.waiting_code)
async def av_got_code(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    code = message.text.strip().upper()
    if not code.replace("_", "").replace("-", "").isalnum() or len(code) < 3:
        await message.answer("⚠️ Noto'g'ri format. Qaytadan kiriting:")
        return
    if await code_exists(code, "videos") or await code_exists(code, "podcasts"):
        await message.answer(
            f"❌ <b>Bu kod allaqachon mavjud: <code>{code}</code></b>\n\n"
            "Boshqa noyob kod kiriting:", parse_mode="HTML",
        )
        return
    await state.update_data(code=code)
    await state.set_state(AddVideo.waiting_category)
    await message.answer(
        "4-qadam: 📂 <b>Kategoriya</b> tanlang:\n\n"
        "• <code>interview</code>\n"
        "• <code>mindset</code>\n"
        "• <code>business</code>\n"
        "• <code>motivation</code>",
        parse_mode="HTML",
    )


@fsm_router.message(AddVideo.waiting_category)
async def av_got_category(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    cat = message.text.strip().lower()
    if cat not in {"interview", "mindset", "business", "motivation"}:
        await message.answer("⚠️ Noto'g'ri. Qaytadan kiriting:")
        return
    await state.update_data(category=cat)
    await state.set_state(AddVideo.waiting_vip)
    await message.answer(
        "5-qadam: 💎 VIP uchunmi?\n\n<b>ha</b> — faqat VIP\n<b>yo'q</b> — hamma",
        parse_mode="HTML",
    )


@fsm_router.message(AddVideo.waiting_vip)
async def av_got_vip(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    is_vip_val = message.text.strip().lower() in ("ha", "yes", "1")
    data = await state.get_data()
    await state.clear()
    video = await add_video(
        code=data["code"], title=data["title"],
        file_id=data["file_id"], category=data["category"],
        is_vip=is_vip_val, added_by=message.from_user.id,
    )
    await message.answer(
        f"✅ <b>Video qo'shildi!</b>\n\n"
        f"🔑 Kod: <code>{video['code']}</code>\n"
        f"🎬 Nom: <b>{video['title']}</b>\n"
        f"📂 Kategoriya: {video['category']}\n"
        f"💎 {'🔒 VIP' if is_vip_val else '🔓 Ochiq'}",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


# ════════════════════════════════════════════════════════════════════════════
# 🎙 PODCAST QO'SHISH
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "🎙 Podcast qo'shish")
async def start_add_podcast(message: Message, state: FSMContext) -> None:
    await state.set_state(AddPodcast.waiting_file)
    await message.answer(
        "🎙 <b>Yangi podcast qo'shish</b>\n\n1-qadam: Audio faylini yuboring 👇",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(AddPodcast.waiting_file, F.audio | F.voice)
async def ap_got_file(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    file_id = message.audio.file_id if message.audio else message.voice.file_id
    await state.update_data(file_id=file_id)
    await state.set_state(AddPodcast.waiting_title)
    await message.answer("2-qadam: ✏️ Podcast <b>nomini</b> kiriting:", parse_mode="HTML")


@fsm_router.message(AddPodcast.waiting_file)
async def ap_bad_file(message: Message) -> None:
    if not is_admin_id(message.from_user.id): return
    await message.answer("⚠️ Audio yoki ovoz xabarini yuboring.")


@fsm_router.message(AddPodcast.waiting_title)
async def ap_got_title(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddPodcast.waiting_code)
    await message.answer(
        "3-qadam: 🔑 <b>Noyob kod</b>:\n<i>Masalan: <code>POD001</code></i>",
        parse_mode="HTML",
    )


@fsm_router.message(AddPodcast.waiting_code)
async def ap_got_code(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    code = message.text.strip().upper()
    if not code.replace("_", "").replace("-", "").isalnum() or len(code) < 3:
        await message.answer("⚠️ Noto'g'ri format. Qaytadan kiriting:")
        return
    if await code_exists(code, "videos") or await code_exists(code, "podcasts"):
        await message.answer(f"❌ <code>{code}</code> allaqachon mavjud. Boshqa kod:", parse_mode="HTML")
        return
    await state.update_data(code=code)
    await state.set_state(AddPodcast.waiting_vip)
    await message.answer("4-qadam: 💎 VIP uchunmi?\n\n<b>ha</b> / <b>yo'q</b>", parse_mode="HTML")


@fsm_router.message(AddPodcast.waiting_vip)
async def ap_got_vip(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    is_vip_val = message.text.strip().lower() in ("ha", "yes", "1")
    data = await state.get_data()
    await state.clear()
    podcast = await add_podcast(
        code=data["code"], title=data["title"],
        file_id=data["file_id"], is_vip=is_vip_val,
        added_by=message.from_user.id,
    )
    await message.answer(
        f"✅ <b>Podcast qo'shildi!</b>\n\n"
        f"🔑 Kod: <code>{podcast['code']}</code>\n"
        f"🎙 Nom: <b>{podcast['title']}</b>\n"
        f"💎 {'🔒 VIP' if is_vip_val else '🔓 Ochiq'}",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


# ════════════════════════════════════════════════════════════════════════════
# 🔥 SHORT QO'SHISH
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "🔥 Short qo'shish")
async def start_add_short(message: Message, state: FSMContext) -> None:
    await state.set_state(AddShort.waiting_title)
    await message.answer(
        "🔥 <b>Yangi Short qo'shish</b>\n\n1-qadam: Sarlavhani kiriting:",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(AddShort.waiting_title)
async def as_got_title(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddShort.waiting_text)
    await message.answer("2-qadam: 📝 Short <b>matnini</b> kiriting:", parse_mode="HTML")


@fsm_router.message(AddShort.waiting_text)
async def as_got_text(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    data = await state.get_data()
    await state.clear()
    short = await add_short(title=data["title"], text=message.text.strip())
    await message.answer(
        f"✅ <b>Short qo'shildi!</b>\n\n"
        f"🔥 Sarlavha: <b>{short['title']}</b>\n"
        f"📌 ID: #{short['id']}",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


# ════════════════════════════════════════════════════════════════════════════
# 🗑 VIDEO O'CHIRISH
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "🗑 Video o'chirish")
async def start_delete_video(message: Message, state: FSMContext) -> None:
    await state.set_state(DeleteVideoState.waiting_code)
    await message.answer(
        "🗑 <b>Video o'chirish</b>\n\nVideo <b>kodini</b> kiriting:",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(DeleteVideoState.waiting_code)
async def dv_got_code(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    code = message.text.strip().upper()
    await state.clear()
    deleted = await delete_video(code)
    if deleted:
        await message.answer(f"✅ <code>{code}</code> o'chirildi.", parse_mode="HTML", reply_markup=admin_menu_kb())
    else:
        await message.answer(f"❌ <code>{code}</code> topilmadi.", parse_mode="HTML", reply_markup=admin_menu_kb())


# ════════════════════════════════════════════════════════════════════════════
# 📢 BROADCAST
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "📢 Broadcast")
async def start_broadcast(message: Message, state: FSMContext) -> None:
    await state.set_state(BroadcastStates.waiting_message)
    await message.answer(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yuboring.\n"
        "<i>Matn, rasm, video — istalgan format.</i>",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(BroadcastStates.waiting_message)
async def bc_got_message(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.update_data(msg_id=message.message_id, chat_id=message.chat.id)
    await state.set_state(BroadcastStates.waiting_confirm)
    await message.answer(
        "⚠️ <b>Tasdiqlash</b>\n\n"
        "Xabar <b>barcha</b> foydalanuvchilarga yuboriladi.\n\n"
        "<b>ha</b> — yuborish  |  <b>yo'q</b> — bekor",
        parse_mode="HTML",
    )


@fsm_router.message(BroadcastStates.waiting_confirm)
async def bc_confirm(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    if message.text.strip().lower() not in ("ha", "yes"):
        await state.clear()
        await message.answer("❌ Broadcast bekor qilindi.", reply_markup=admin_menu_kb())
        return
    data = await state.get_data()
    await state.clear()
    status = await message.answer("⏳ <b>Broadcast boshlandi...</b>", parse_mode="HTML")
    try:
        original = await message.bot.forward_message(
            chat_id=message.chat.id,
            from_chat_id=data["chat_id"],
            message_id=data["msg_id"],
        )
        success, fail = await broadcast(message.bot, original)
        await original.delete()
    except Exception as e:
        await status.edit_text(f"❌ Xatolik: {e}")
        return
    await status.edit_text(
        f"✅ <b>Broadcast yakunlandi!</b>\n\n"
        f"✉️ Yuborildi: <b>{success}</b>\n"
        f"❌ Xato: <b>{fail}</b>",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


# ════════════════════════════════════════════════════════════════════════════
# 📊 STATISTIKA
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    stats = await get_full_stats()
    await message.answer(stats_text(stats), parse_mode="HTML", reply_markup=admin_menu_kb())


# ════════════════════════════════════════════════════════════════════════════
# 👑 VIP BERISH / OLISH
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "👑 VIP berish")
async def start_grant_vip(message: Message, state: FSMContext) -> None:
    await state.set_state(GrantVIPState.waiting_user_id)
    await message.answer(
        "👑 <b>VIP berish</b>\n\nFoydalanuvchi <b>Telegram ID</b>sini kiriting:",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(GrantVIPState.waiting_user_id)
async def do_grant_vip(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.clear()
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Faqat raqam kiriting.")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("❌ Bu ID li foydalanuvchi topilmadi.", parse_mode="HTML")
        return
    await grant_vip(uid)
    try:
        from services.settings_service import get_admin_username
        uname = await get_admin_username()
        contact = f"@{uname}" if uname else "admin"
        await message.bot.send_message(
            uid,
            "👑 <b>Tabriklaymiz!</b>\n\n"
            "Admin tomonidan sizga <b>VIP a'zolik</b> berildi!\n"
            "Barcha eksklyuziv kontentlarga to'liq kirish imkoniyatingiz bor.\n\n"
            f"Savollar uchun: {contact}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await message.answer(
        f"✅ <b>{user['full_name']}</b> (<code>{uid}</code>) ga VIP berildi.",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


@router.message(IsAdmin(), F.text == "❌ VIP olish")
async def start_revoke_vip(message: Message, state: FSMContext) -> None:
    await state.set_state(RevokeVIPState.waiting_user_id)
    await message.answer(
        "❌ <b>VIP olish</b>\n\nFoydalanuvchi <b>Telegram ID</b>sini kiriting:",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(RevokeVIPState.waiting_user_id)
async def do_revoke_vip(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.clear()
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Noto'g'ri ID.")
        return
    user = await get_user(uid)
    name = user["full_name"] if user else str(uid)
    await revoke_vip(uid)
    await message.answer(
        f"✅ <b>{name}</b> (<code>{uid}</code>) VIP maqomidan mahrum qilindi.",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )


# ════════════════════════════════════════════════════════════════════════════
# ⚙️ ADMIN USERNAME
# ════════════════════════════════════════════════════════════════════════════

@router.message(IsAdmin(), F.text == "⚙️ Admin username")
async def start_set_username(message: Message, state: FSMContext) -> None:
    current = await get_admin_username()
    c_line  = f"@{current}" if current else "⚠️ Hali o'rnatilmagan"
    await state.set_state(SetUsernameState.waiting_username)
    await message.answer(
        f"⚙️ <b>Admin username</b>\n\n"
        f"Hozirgi: <b>{c_line}</b>\n\n"
        "Yangi username ni yuboring (@ belgisisiz):\n"
        "<i>Masalan: <code>shohrux_admin</code></i>",
        parse_mode="HTML", reply_markup=cancel_kb(),
    )


@fsm_router.message(SetUsernameState.waiting_username)
async def do_set_username(message: Message, state: FSMContext) -> None:
    if not is_admin_id(message.from_user.id): return
    await state.clear()
    raw = (message.text or "").strip().lstrip("@")
    if not raw or " " in raw:
        await message.answer("⚠️ Noto'g'ri username.", reply_markup=admin_menu_kb())
        return
    await set_setting("admin_username", raw)
    await message.answer(
        f"✅ <b>Username o'rnatildi: @{raw}</b>\n\n"
        "Barcha foydalanuvchi xabarlarida ko'rinadi.",
        parse_mode="HTML", reply_markup=admin_menu_kb(),
    )
