"""
utils/texts.py — Premium bot xabarlari (async, dinamik)

Barcha funksiyalar await bilan chaqiriladi.
Admin username DBdan real-time olinadi.
"""

from config import cfg


# ─── YORDAMCHI ────────────────────────────────────────────────────────────────

async def _uname() -> str:
    from services.settings_service import get_admin_username
    return await get_admin_username()


async def _contact() -> str:
    u = await _uname()
    return f"📩 Murojaat: @{u}" if u else "📩 <i>Admin hozircha mavjud emas</i>"


async def get_contact_kb(label: str = "📩 Admin bilan bog'lanish"):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    u = await _uname()
    if not u:
        return None
    b = InlineKeyboardBuilder()
    b.button(text=label, url=f"https://t.me/{u}")
    return b.as_markup()


async def get_vip_kb():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    u = await _uname()
    t = cfg.REFERRAL_VIP_THRESHOLD
    b = InlineKeyboardBuilder()
    if u:
        b.button(text="💳 To'lov orqali VIP olish",
                 url=f"https://t.me/{u}")
    b.button(text=f"🎁 Bepul VIP — {t} ta do'st taklif qiling",
             callback_data="referral_info")
    if u:
        b.button(text="💬 Admin bilan bog'lanish",
                 url=f"https://t.me/{u}")
    b.adjust(1)
    return b.as_markup()


async def get_vip_locked_kb():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    u = await _uname()
    b = InlineKeyboardBuilder()
    b.button(text="💎 VIP olish", callback_data="show_vip")
    if u:
        b.button(text="💬 Admin", url=f"https://t.me/{u}")
    b.adjust(2)
    return b.as_markup()


# ─── XUSH KELIBSIZ ────────────────────────────────────────────────────────────

async def welcome_text(name: str) -> str:
    c = await _contact()
    return (
        f"👑 <b>Xush kelibsiz, {name}!</b>\n\n"
        "Siz <b>Milliarderlar Klubi</b> — Telegram'dagi\n"
        "eng noyob bilim platformasiga qadm qo'ydingiz.\n\n"
        "┌─────────────────────────┐\n"
        "│  Bu yerda siz olasiz:   │\n"
        "└─────────────────────────┘\n"
        "🎬  Dunyo milliardyorlari intervyulari\n"
        "🧠  Boylar fikrlash tarzining sirlari\n"
        "📈  Investitsiya va biznes strategiyalari\n"
        "🔥  Har kuni yangi motivatsiya va bilim\n"
        "💎  VIP a'zolarga eksklyuziv kontent\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>💡 Bilim — eng qimmatli investitsiya.\n"
        "   Bugun boshlang, ertaga natija ko'ring.</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


async def welcome_referred_text(name: str) -> str:
    c = await _contact()
    return (
        f"🎉 <b>Xush kelibsiz, {name}!</b>\n\n"
        "Do'stingiz tavsiyasi orqali siz\n"
        "<b>Milliarderlar Klubi</b>ga qo'shildingiz!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 Bu — oddiy bot emas.\n"
        "Bu <b>yashirin bilim va muvaffaqiyat\n"
        "platformasi</b> — faqat maqsadli insonlar uchun.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Quyidagi menyudan boshlang 👇\n\n"
        f"{c}"
    )


# ─── VIP ──────────────────────────────────────────────────────────────────────

async def vip_info_text() -> str:
    c = await _contact()
    t = cfg.REFERRAL_VIP_THRESHOLD
    return (
        "╔═══════════════════════════╗\n"
        "║  👑  VIP  A'ZOLIK  👑  ║\n"
        "║  Milliarderlar Klubi      ║\n"
        "╚═══════════════════════════╝\n\n"
        "<b>Oddiy a'zolar faqat namunani ko'radi.\n"
        "VIP a'zolar — hammasini.</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 <b>VIP A'ZOLARGA BERILADIGAN NARSALAR:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎬  <b>200+ eksklyuziv to'liq intervyu</b>\n"
        "    Elon Musk · Jeff Bezos · W. Buffett\n"
        "    Bill Gates · Steve Jobs · Ray Dalio\n\n"
        "🎙  <b>Premium podcastlar arxivi</b>\n"
        "    Biznes · Investitsiya · Psixologiya\n\n"
        "🧠  <b>Milliarder aqli — maxsus kurs</b>\n"
        "    Real hayotdan olingan saboqlar\n\n"
        "📈  <b>Haftalik yangi kontent</b>\n"
        "    Boshqalar bilmasidan oldin\n\n"
        "🚫  <b>Hech qanday reklama</b>\n"
        "    Faqat sof, toza bilim\n\n"
        "💬  <b>VIP yopiq guruh</b>\n"
        "    Bir xil fikrdagilar bilan muloqot\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎁 <b>BEPUL VIP OLISH YO'LI:</b>\n"
        f"   {t} ta do'stingizni taklif qiling\n"
        "   → VIP avtomatik beriladi!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{c}\n\n"
        "⬇️  <b>Tanlang:</b>"
    )


async def vip_locked_text() -> str:
    c = await _contact()
    t = cfg.REFERRAL_VIP_THRESHOLD
    return (
        "🔒 <b>Bu kontent VIP a'zolar uchun</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Siz ham bu bilimga ega bo'lishingiz mumkin!\n\n"
        f"🎁 <b>BEPUL:</b> {t} ta do'st taklif qiling\n"
        f"💳 <b>TO'LOV:</b> Admin orqali aktivlashtiring\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


async def vip_granted_text() -> str:
    c = await _contact()
    return (
        "👑 <b>TABRIKLAYMIZ! VIP BERILDI!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Siz endi <b>Milliarderlar Klubi VIP</b>\n"
        "a'zosisiniz! 🎉\n\n"
        "✅ Barcha eksklyuziv videolar\n"
        "✅ To'liq podcast arxivi\n"
        "✅ Haftalik yangi kontent\n"
        "✅ VIP yopiq guruh\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


# ─── REFERRAL ─────────────────────────────────────────────────────────────────

async def referral_info_text(link: str, count: int) -> str:
    c = await _contact()
    t         = cfg.REFERRAL_VIP_THRESHOLD
    done      = min(count, t)
    remaining = max(0, t - count)
    bar       = "🟡" * done + "⚫️" * remaining

    if count >= t:
        status = "✅ <b>VIP oldingiz! Tabriklaymiz!</b>"
    elif remaining == 1:
        status = "🔥 <b>Oxirgi 1 ta qoldi — VIP yaqin!</b>"
    elif remaining <= 3:
        status = f"⚡️ Yana <b>{remaining} ta</b> taklif qiling!"
    else:
        status = f"⏳ Yana <b>{remaining} ta</b> taklif → VIP bepul!"

    return (
        "🔗 <b>Taklif tizimi — Bepul VIP oling!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📎 <b>Sizning havolangiz:</b>\n"
        f"<code>{link}</code>\n"
        "<i>(bosib nusxa olish mumkin)</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 <b>Natija:</b> {bar}\n"
        f"            <b>{count} / {t}</b> ta\n\n"
        f"{status}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 <b>Shartlar:</b>\n"
        "  • Faqat <b>yangi</b> foydalanuvchilar hisoblanadi\n"
        "  • O'zingizni taklif qilib bo'lmaydi\n"
        f"  • {t} ta to'lsa → VIP <b>avtomatik</b> beriladi\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


# ─── KONTENT RO'YXATI ─────────────────────────────────────────────────────────

async def video_list_text(items: list, kind: str) -> str:
    c    = await _contact()
    icon = "🎬" if kind == "video" else "🎙"
    name = "Intervyular" if kind == "video" else "Podcastlar"
    lines = [
        f"{icon} <b>Mavjud {name}:</b>\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    for v in items:
        lock  = "🔒" if v["is_vip"] else "🔓"
        views = v.get("views", 0)
        lines.append(
            f"{lock} <code>{v['code']}</code>  —  <b>{v['title']}</b>\n"
            f"     👁 {views} ko'rilgan"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📌 <b>Kodni yuboring</b> → kontent ochiladi")
    lines.append(f"\n{c}")
    return "\n".join(lines)


async def video_caption_text(title: str, category: str, views: int) -> str:
    c = await _contact()
    cat_icons = {
        "interview":  "🎙 Intervyu",
        "mindset":    "🧠 Mindset",
        "business":   "💼 Biznes",
        "motivation": "🔥 Motivatsiya",
        "Podcast":    "🎙 Podcast",
    }
    cat_label = cat_icons.get(category, f"📂 {category}")
    return (
        f"🎬 <b>{title}</b>\n\n"
        f"{cat_label}  •  👁 {views:,} ko'rilgan\n\n"
        f"{c}"
    )


async def no_content_text() -> str:
    c = await _contact()
    return (
        "📭 <b>Hozircha kontent yo'q</b>\n\n"
        "Tez orada yangi material qo'shiladi.\n\n"
        f"{c}"
    )


async def not_found_text() -> str:
    c = await _contact()
    return (
        "❌ <b>Bunday kod topilmadi</b>\n\n"
        "Kodni to'g'ri kiritganingizga ishonch hosil qiling.\n"
        "Barcha videolarni ko'rish: <b>🎬 Intervyular</b>\n\n"
        f"{c}"
    )


async def search_hint_text() -> str:
    c = await _contact()
    return (
        "🔍 <b>Video / Podcast qidirish</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kontent kodini yuboring.\n\n"
        "📌 <b>Kod qayerdan topiladi?</b>\n"
        "  🎬 Intervyular bo'limida\n"
        "  🎙 Podcastlar bo'limida\n\n"
        "<i>Masalan: <code>ELON001</code></i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


# ─── SHORTS ───────────────────────────────────────────────────────────────────

async def short_card_text(title: str, text: str, num: int, total: int) -> str:
    c = await _contact()
    return (
        f"⚡️ <b>{title}</b>\n\n"
        f"{text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"           <i>— Milliarderlar Klubi</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


async def no_shorts_text() -> str:
    c = await _contact()
    return (
        "📭 <b>Shorts bo'limi hozircha bo'sh</b>\n\n"
        "Tez orada qisqa va kuchli motivatsion\n"
        "kontent qo'shiladi.\n\n"
        f"{c}"
    )


# ─── HAMKORLIK / REKLAMA / BUYURTMA ──────────────────────────────────────────

async def hamkorlik_text() -> str:
    c = await _contact()
    return (
        "🤝 <b>Hamkorlik — Katta Imkoniyat</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Milliarderlar Klubi</b> bilan hamkorlik\n"
        "qiling va 50,000+ maqsadli auditoriyaga\n"
        "yeting.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎙 <b>Podcast buyurtma</b>\n"
        "   Biznesingiz haqida professional podcast\n\n"
        "🎬 <b>Intervyu buyurtma</b>\n"
        "   Shaxsiy yoki kompaniya eksklyuziv suhbati\n\n"
        "🤝 <b>Uzoq muddatli hamkorlik</b>\n"
        "   Doimiy brend integratsiyasi\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 50,000+ faol a'zo  •  Premium auditoriya\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


async def reklama_text() -> str:
    c = await _contact()
    return (
        "📢 <b>Reklama — Maqsadli Auditoriyaga Yeting</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 <b>Auditoriya portret:</b>\n"
        "   • 50,000+ faol foydalanuvchi\n"
        "   • Yosh: 18–45 | Aktiv iste'molchilar\n"
        "   • Qiziqish: biznes, investitsiya, o'sish\n\n"
        "📦 <b>Reklama formatlari:</b>\n"
        "   • 📝 Matn + rasm (post)\n"
        "   • 🎥 Video reklama\n"
        "   • 📌 Pinlangan post (24 soat)\n"
        "   • ✍️ Native kontent (tavsiya)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


async def buyurtma_text() -> str:
    c = await _contact()
    return (
        "📦 <b>Buyurtma Berish</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi xizmatlarni buyurtma qilishingiz\n"
        "mumkin:\n\n"
        "🎙 Podcast yozib olish\n"
        "🎬 Intervyu formatlash\n"
        "📝 Skript va matn yozish\n"
        "🎨 Kontent dizayn\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Narx va shartlar uchun adminга yozing:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{c}"
    )


# ─── ADMIN STATISTIKA ─────────────────────────────────────────────────────────

def stats_text(s: dict) -> str:
    top     = s.get("top_video")
    top_str = (
        f"<b>{top['title']}</b>\n"
        f"     👁 {top['views']:,} ko'rish"
    ) if top else "Hali yo'q"

    conv = round(s['vip_users'] / s['total_users'] * 100, 1) if s['total_users'] else 0

    return (
        "📊 <b>STATISTIKA PANELI</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 <b>FOYDALANUVCHILAR</b>\n"
        f"   Jami:        <b>{s['total_users']:,}</b>\n"
        f"   Bugun:       <b>+{s['today_users']}</b>\n"
        f"   VIP:         <b>{s['vip_users']}</b>\n"
        f"   Konversiya:  <b>{conv}%</b>\n\n"
        "🎬 <b>KONTENT</b>\n"
        f"   Videolar:    <b>{s['total_videos']}</b>\n"
        f"   Podcastlar:  <b>{s['total_podcasts']}</b>\n"
        f"   Shorts:      <b>{s['total_shorts']}</b>\n"
        f"   Ko'rishlar:  <b>{s['total_views']:,}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>TOP VIDEO:</b>\n"
        f"   {top_str}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
