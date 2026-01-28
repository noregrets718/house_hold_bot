"""Reporting handlers."""

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app import db
from app.utils.months import parse_month, get_month_name

router = Router()


def parse_month_year(args: str | None) -> tuple[int | None, int | None, str | None]:
    """
    Parse month and optional year from command arguments.
    Returns (month, year, error_message).
    """
    if not args:
        return None, None, "Укажите месяц."

    parts = args.strip().split()
    if not parts:
        return None, None, "Укажите месяц."

    month = parse_month(parts[0])
    if month is None:
        return None, None, f"Неизвестный месяц: {parts[0]}"

    if len(parts) >= 2:
        try:
            year = int(parts[1])
        except ValueError:
            return None, None, f"Неверный формат года: {parts[1]}"
    else:
        year = datetime.now().year

    return month, year, None


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Welcome message."""
    await message.answer(
        "Бот для учёта ежемесячных пожертвований.\n\n"
        "Используйте /help для списка команд."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """List available commands."""
    await message.answer(
        "Доступные команды:\n\n"
        "/add_donor ФАМИЛИЯ - добавить донора\n"
        "/remove_donor ФАМИЛИЯ - удалить донора\n"
        "/donors - список всех доноров\n\n"
        "/paid МЕСЯЦ [ГОД] - кто оплатил\n"
        "/unpaid МЕСЯЦ [ГОД] - кто не оплатил\n"
        "/history ФАМИЛИЯ - история оплат донора\n"
        "/delete ФАМИЛИЯ МЕСЯЦ [ГОД] - удалить запись об оплате\n\n"
        "Для записи оплаты отправьте сообщение в формате:\n"
        "Фамилия\n"
        "Месяц [Год]"
    )


@router.message(Command("paid"))
async def cmd_paid(message: Message, command: CommandObject):
    """List donors who paid for a month."""
    month, year, error = parse_month_year(command.args)
    if error:
        await message.answer(error)
        return

    donors = await db.get_paid_donors(month, year)

    if not donors:
        await message.answer(f"Никто не оплатил за {get_month_name(month)} {year}.")
        return

    lines = [f"Оплатили за {get_month_name(month)} {year}:"]
    for i, donor in enumerate(donors, 1):
        lines.append(f"{i}. {donor['last_name']}")

    await message.answer("\n".join(lines))


@router.message(Command("unpaid"))
async def cmd_unpaid(message: Message, command: CommandObject):
    """List donors who haven't paid for a month."""
    month, year, error = parse_month_year(command.args)
    if error:
        await message.answer(error)
        return

    donors = await db.get_unpaid_donors(month, year)

    if not donors:
        await message.answer(f"Все оплатили за {get_month_name(month)} {year}!")
        return

    lines = [f"Не оплатили за {get_month_name(month)} {year}:"]
    for i, donor in enumerate(donors, 1):
        lines.append(f"{i}. {donor['last_name']}")

    await message.answer("\n".join(lines))


@router.message(Command("history"))
async def cmd_history(message: Message, command: CommandObject):
    """Show payment history for a donor."""
    if not command.args:
        await message.answer("Использование: /history ФАМИЛИЯ")
        return

    last_name = command.args.strip()
    donor = await db.get_donor(last_name)

    if not donor:
        await message.answer(f"Донор {last_name} не найден.")
        return

    history = await db.get_donor_history(donor["id"])

    if not history:
        await message.answer(f"У донора {last_name} нет записей об оплатах.")
        return

    lines = [f"История оплат {last_name}:"]
    for record in history:
        month_name = get_month_name(record["month"])
        lines.append(f"• {month_name} {record['year']}")

    await message.answer("\n".join(lines))


@router.message(Command("delete"))
async def cmd_delete(message: Message, command: CommandObject):
    """Delete a payment record."""
    if not command.args:
        await message.answer("Использование: /delete ФАМИЛИЯ МЕСЯЦ [ГОД]")
        return

    parts = command.args.strip().split()
    if len(parts) < 2:
        await message.answer("Использование: /delete ФАМИЛИЯ МЕСЯЦ [ГОД]")
        return

    last_name = parts[0]
    month_args = " ".join(parts[1:])

    month, year, error = parse_month_year(month_args)
    if error:
        await message.answer(error)
        return

    donor = await db.get_donor(last_name)
    if not donor:
        await message.answer(f"Донор {last_name} не найден.")
        return

    if await db.delete_payment(donor["id"], month, year):
        await message.answer(
            f"Запись удалена: {last_name}, {get_month_name(month)} {year}"
        )
    else:
        await message.answer(
            f"Запись не найдена: {last_name}, {get_month_name(month)} {year}"
        )
