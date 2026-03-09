import logging

from aiogram import Router
from aiogram.types import Message

from src.services.query_service import process_query

logger = logging.getLogger(__name__)
router = Router()


@router.message()
async def handle_message(message: Message) -> None:
    if not message.text:
        await message.answer("Отправьте текстовый запрос.")
        return

    logger.info("Запрос от %s: %s", message.from_user.id, message.text)
    result = await process_query(message.text)
    await message.answer(result)
