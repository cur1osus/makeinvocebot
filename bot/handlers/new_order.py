from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datetime import datetime

from aiogram import Router
from aiogram.types import FSInputFile
import os
from bot.db.models import UserDB, ChatDB, MessageDB
from bot.utils import fn, generate_invoice
import uuid

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
logger = logging.getLogger(__name__)


prompt = """Структурируй этот заказ в виде json для дальнейшей обработки и составления накладной, отправь только json без дополнительного текста, проставь стоимость по
этому списку:

Пример результата
{
  "order": {
    "date": "18.07",
    "city": "Макеевка",
    "address": "ул. Циолковского, д. 13",
    "phone": "+79494176220",
    "items": [
        {"name": "Блины Жульен  ", "quantity": "2", "unit": "кг"},
        {"name": "Блины с мясом", "quantity": "2", "unit": "кг"},
        {"name": "Блины трио", "quantity": "1", "unit": "кг"},
        {"name": "Куриные рулетики с сыром", "quantity": "1.5", "unit": "кг"},
        {"name": "Жульен", "quantity": "3", "unit": "шт"}
    ],
    "total_from_text": "5445"
  }
}

если в тексте нет конечной стоимости не добовляй total_from_text
"""


@router.message()
async def get_order(
    message: Message,
    user: UserDB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if user is None and message.from_user:
        await message.answer("Пожалуйста, нажмите кнопку /start для авторизации")
        return
    order = message.text or ""

    chat = ChatDB(chat_name=uuid.uuid4())
    system_prompt = {"role": "system", "content": prompt}
    user_prompt = {"role": "user", "content": order}
    chain_messages = [system_prompt, user_prompt]
    answer = fn.get_answer(chain_messages)

    filename = None
    try:
        filename = generate_invoice(answer)
        await message.answer_document(document=FSInputFile(path=filename))
    except Exception as e:
        await message.answer(f"Не смог сгенерировать накладную, ошибка: {e}")

    message_db = MessageDB(content=order, timestamp=datetime.now().timestamp(), role="user")
    message_db_from_assistant = MessageDB(content=answer, timestamp=datetime.now().timestamp(), role="assistant")
    chat.messages.append(message_db)
    chat.messages.append(message_db_from_assistant)
    user.chats.append(chat)
    if filename:
        os.remove(filename)
    await session.commit()
