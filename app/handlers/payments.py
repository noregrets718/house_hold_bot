"""Payment recording handler via plain messages."""

import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from app import db
from app.utils.months import parse_month, get_month_name

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def record_payment(message: Message):
    """
    Record payment from message format:
    Фамилия
    Месяц [Год]
    """
    text = message.text.strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if len(lines) != 2:
        # Not a payment format, ignore
        return

    last_name = lines[0]
    month_line = lines[1]

    # Parse month and optional year
    parts = month_line.split()
    if not parts:
        return

    month = parse_month(parts[0])
    if month is None:
        await message.answer(f"Неизвестный месяц: {parts[0]}")
        return

    # Parse year if provided
    if len(parts) >= 2:
        try:
            year = int(parts[1])
        except ValueError:
            await message.answer(f"Неверный формат года: {parts[1]}")
            return
    else:
        year = datetime.now().year

    # Find donor
    donor = await db.get_donor(last_name)
    if not donor:
        await message.answer(f"Донор {last_name} не найден.")
        return

    # Record payment
    recorded_by = message.from_user.id if message.from_user else 0

    if await db.record_payment(donor["id"], month, year, recorded_by):
        await message.answer(
            f"Оплата записана: {last_name}, {get_month_name(month)} {year}"
        )
    else:
        await message.answer(
            f"Оплата уже записана: {last_name}, {get_month_name(month)} {year}"
        )
