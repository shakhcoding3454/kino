"""
config.py — Markaziy konfiguratsiya

Railway: environment variable lar orqali.
Local: .env fayl orqali (python-dotenv).
"""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Config:
    # ── Bot ───────────────────────────────────────────────────────────────────
    BOT_TOKEN: str
    API_ID:    int
    API_HASH:  str

    # ── Admin ─────────────────────────────────────────────────────────────────
    ADMIN_IDS:      tuple
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # ── Database ──────────────────────────────────────────────────────────────
    DB_PATH: str

    # ── Server ────────────────────────────────────────────────────────────────
    PORT: int

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int
    RATE_LIMIT_WINDOW:   float

    # ── Referral ──────────────────────────────────────────────────────────────
    REFERRAL_VIP_THRESHOLD: int

    # ── Runtime ───────────────────────────────────────────────────────────────
    ENV: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "8001689680:AAFJQkecqkAHRhnB_wkdxURjtELffQ4skAw").strip()

    raw = os.getenv("ADMIN_IDS", "").strip()
    admin_ids = tuple(
        int(x.strip()) for x in raw.split(",") if x.strip().isdigit()
    )

    # Railway /data persistent volume, local ./data
    default_db = "/data/bot.db" if os.path.exists("/data") else "data/bot.db"

    return Config(
        BOT_TOKEN=token,
        API_ID=int(os.getenv("API_ID", "39897939")),
        API_HASH=os.getenv("API_HASH", "4ea755dc16b379cf11cc5a171fac3272").strip(),

        ADMIN_IDS=admin_ids,
        ADMIN_USERNAME=os.getenv("ADMIN_USERNAME", "milliarderlar_admin").strip(),
        ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD", "klub2026").strip(),

        DB_PATH=os.getenv("DB_PATH", default_db),
        PORT=int(os.getenv("PORT", "8080")),

        RATE_LIMIT_REQUESTS=int(os.getenv("RATE_LIMIT_REQUESTS", "3")),
        RATE_LIMIT_WINDOW=float(os.getenv("RATE_LIMIT_WINDOW", "2.0")),

        REFERRAL_VIP_THRESHOLD=int(os.getenv("REFERRAL_VIP_THRESHOLD", "10")),
        ENV=os.getenv("RAILWAY_ENVIRONMENT", os.getenv("ENV", "development")),
    )


cfg = load_config()
