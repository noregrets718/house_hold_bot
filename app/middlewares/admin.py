"""Admin check middleware."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.config import settings
from app import db


class AdminMiddleware(BaseMiddleware):
    """Middleware that checks if user is an admin."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None

        if user_id is None:
            return None

        # Check if user is in config admin list
        if user_id in settings.admin_ids:
            return await handler(event, data)

        # Check if user is in database admins
        if await db.is_admin_in_db(user_id):
            return await handler(event, data)

        # Not an admin - reject
        await event.answer("У вас нет доступа к этому боту.")
        return None
