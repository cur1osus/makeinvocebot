from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart

from bot.db.models import UserDB

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def start_cmd_with_deep_link(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    args = command.args.split() if command.args else []
    deep_link = args[0]
    if deep_link:
        await message.answer("Deep link received!")


@router.message(CommandStart(deep_link=False))
async def start_cmd(
    message: Message,
    user: UserDB | None,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if user is None and message.from_user:
        full_name = message.from_user.full_name
        username = message.from_user.username or "none"
        new_user = UserDB(name=full_name, username=username, user_id=message.from_user.id)
        session.add(new_user)
        await session.commit()
    await message.answer("Привет, отправь мне заказ, и я отправлю накладную!")
