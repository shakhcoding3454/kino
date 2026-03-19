"""utils/filters.py — Admin filterlari."""

import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import cfg

logger = logging.getLogger(__name__)

# Parol orqali kirgan adminlar (restart da tozalanadi)
_session_admins: set[int] = set()


def add_session_admin(uid: int) -> None:
    _session_admins.add(uid)
    logger.info("Session admin qo'shildi: %s", uid)


def remove_session_admin(uid: int) -> None:
    _session_admins.discard(uid)


def is_admin_id(uid: int) -> bool:
    return uid in cfg.ADMIN_IDS or uid in _session_admins


class IsAdmin(BaseFilter):
    """Message va CallbackQuery uchun ishlaydi."""
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return user is not None and is_admin_id(user.id)
