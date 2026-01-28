"""Donor management handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app import db

router = Router()


@router.message(Command("add_donor"))
async def cmd_add_donor(message: Message, command: CommandObject):
    """Add a new donor."""
    if not command.args:
        await message.answer("Использование: /add_donor ФАМИЛИЯ")
        return

    last_name = command.args.strip()
    if not last_name:
        await message.answer("Укажите фамилию донора.")
        return

    if await db.add_donor(last_name):
        await message.answer(f"Донор {last_name} добавлен.")
    else:
        await message.answer(f"Донор {last_name} уже существует.")


@router.message(Command("add_many"))
async def cmd_add_many(message: Message, command: CommandObject):
    """Add multiple donors at once."""
    if not command.args:
        await message.answer("Использование: /add_many ФАМИЛИЯ1 ФАМИЛИЯ2 ФАМИЛИЯ3 ...")
        return

    last_names = command.args.split()
    if not last_names:
        await message.answer("Укажите фамилии доноров через пробел.")
        return

    added, existed = await db.add_donors_many(last_names)

    lines = []
    if added:
        lines.append(f"Добавлены: {', '.join(added)}")
    if existed:
        lines.append(f"Уже существуют: {', '.join(existed)}")

    await message.answer("\n".join(lines) if lines else "Ничего не добавлено.")


@router.message(Command("remove_donor"))
async def cmd_remove_donor(message: Message, command: CommandObject):
    """Remove a donor."""
    if not command.args:
        await message.answer("Использование: /remove_donor ФАМИЛИЯ")
        return

    last_name = command.args.strip()
    if not last_name:
        await message.answer("Укажите фамилию донора.")
        return

    if await db.remove_donor(last_name):
        await message.answer(f"Донор {last_name} удалён.")
    else:
        await message.answer(f"Донор {last_name} не найден.")


@router.message(Command("donors"))
async def cmd_donors(message: Message):
    """List all donors."""
    donors = await db.get_all_donors()

    if not donors:
        await message.answer("Список доноров пуст.")
        return

    lines = ["Список доноров:"]
    for i, donor in enumerate(donors, 1):
        lines.append(f"{i}. {donor['last_name']}")

    await message.answer("\n".join(lines))
