from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters.command import CommandStart
from aiogram.types import Message
from html import escape

from data.config import group_id

router = Router()


@router.message(CommandStart())
async def get_start_command_handler(message: Message):
    user_name = escape(message.from_user.first_name)

    alert = ''
    if message.chat.id != message.from_user.id:
        if message.chat.id != group_id:
            alert = 'Бот не будет работать в вашей группе!'
        else:
            admin_rights = await message.bot.get_chat_member(group_id, message.bot.id)
            if admin_rights.status not in (ChatMemberStatus.ADMINISTRATOR,
                                           ChatMemberStatus.CREATOR):
                alert = 'Бот не будет работать без прав администратора!'
            elif not admin_rights.can_invite_users:
                alert = 'Бот не будет работать без права на приглашение участников!'
            elif not admin_rights.can_pin_messages:
                alert = 'Бот не будет работать без права на закрепление сообщений!'
            elif not admin_rights.can_delete_messages:
                alert = 'Выдайте право на удаление сообщений, если хотите, чтобы бот удалял системные сообщения о закреплении заявки!'
    
    if alert:
        alert = f'  — ⚠️ {alert}'

    await message.answer(
        f'Привет, <i>{user_name}</i>! Я МЭШ Guard бот, я принимаю заявки и защищаю чат от ДИТевцев'
        f'\n{alert}'
    )
