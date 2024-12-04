from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ContentType

router = Router()


@router.message(F.content_type == ContentType.PINNED_MESSAGE)
async def get_pinned_message_handler(message: Message):
    try:
        await message.delete()
    except TelegramBadRequest:
        ...
