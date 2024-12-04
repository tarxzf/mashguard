from aiogram import Router, Bot, F
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ChatJoinRequest, Message, CallbackQuery
from html import escape
from typing import Optional, Literal, List, Tuple

from data.config import group_id, message_thread_id
from keyboards.join_request_keyboard import JoinRequestKeyboard
from loader import storage, database

router = Router()


class JoinRequestState(StatesGroup):
    question_1 = State()
    question_2 = State()


@router.chat_join_request()
async def get_join_request_handler(update: ChatJoinRequest):
    user_id = update.from_user.id
    state = FSMContext(storage, StorageKey(update.bot.id, user_id, user_id))

    admin_rights = await update.bot.get_chat_member(group_id, update.bot.id)
    if admin_rights.status not in (ChatMemberStatus.ADMINISTRATOR,
                                   ChatMemberStatus.CREATOR):
        return
    
    if not (admin_rights.can_invite_users and admin_rights.can_pin_messages):
        return
    
    row: Tuple[bool] = await database.fetchone(
        'SELECT already_sent FROM users WHERE id = %s;',
        (user_id,)
    )
    user_already_sent = row[0] if row else False
    if user_already_sent:
        try:
            await update.bot.send_message(
                user_id,
                '🚫 Вы уже отправляли запрос на добавление в группу!'
                '\n  — Ожидайте решения администрации'
            )
        except TelegramBadRequest:
            ...
        return

    user_name = escape(update.from_user.first_name)
    try:
        application_message = await update.bot.send_message(
            chat_id=user_id,
            text=f'👋 Привет, <i>{user_name}</i>! Чтобы вступить в наш чат тебе нужно ответить на 2 вопроса'
            '\n  — <b>Вопрос 1.</b> Как вы узнали о группе?'
        )
    except TelegramForbiddenError:
        ...
    else:
        user_data = await state.get_data()
        await state.clear()

        message_id: Optional[int] = user_data.get('message_id')
        if message_id is not None:
            try:
                await update.bot.delete_message(user_id, message_id)
            except TelegramBadRequest:
                ...
        
        await state.update_data(message_id=application_message.message_id)
        await state.set_state(JoinRequestState.question_1)


@router.message(JoinRequestState.question_1)
async def get_answer_question_1_text_message_handler(message: Message, state: FSMContext):
    await state.update_data(question_1=message.message_id)

    await message.answer(
        '👍 Отлично!'
        '\n  — <b>Вопрос 2.</b> С какой целью вы подаёте заявку?'
    )
    await state.set_state(JoinRequestState.question_2)


@router.message(JoinRequestState.question_2)
async def get_answer_question_2_text_message_handler(message: Message, state: FSMContext):
    await state.update_data(question_2=message.message_id)
    user_data = await state.get_data()
    await state.clear()

    user_id = message.from_user.id

    status = await _send_application(message.bot, user_id, escape(message.from_user.first_name),
                                     list(user_data.values())[1:3], group_id, message_thread_id)
    
    await database.execute(
        'UPDATE users SET already_sent = true WHERE id = %s;',
        (user_id,)
    )

    if not status:
        await message.answer(
            '✅ Спасибо большое за ответы на наши вопросы!'
            '\n  — Ваша заявка была отправлена на модерацию. Ожидайте'
        )
    else:
        await message.answer(
            '⚠️ Произошла непредвиденная ошибка! Не удалось переслать ответы, возможно они были удалены!'
            '\n  — Подайте заявку снова, и попробуйте ещё раз'
        )


@router.callback_query(F.data.split()[0] == JoinRequestKeyboard.button_callback_1)
async def get_join_request_callback_query_handler(callback: CallbackQuery):
    callback_data = callback.data.split()[1:]
    application_status = callback_data[0]
    user_id = int(callback_data[1])

    admin_rights = await callback.bot.get_chat_member(group_id, callback.from_user.id)
    if admin_rights.status not in (ChatMemberStatus.ADMINISTRATOR,
                                   ChatMemberStatus.CREATOR):
        await callback.answer('❗️ Вы не являетесь администратором!')
        return

    if application_status == JoinRequestKeyboard.button_callback_2.split()[1]:  # approve
        action =  callback.bot.approve_chat_join_request
        status = '✅ Принято'
        text_message = '✅ Ваша заявка была принята!'
    else:  # decline
        action =  callback.bot.decline_chat_join_request
        status = '🚫 Отклонено'
        text_message = '🚫 Ваша заявка была отклонена'
    
    await database.execute(
        'UPDATE users SET already_sent = false WHERE id = %s;',
        (user_id,)
    )
    
    await callback.message.edit_text(
        f'{callback.message.text}'
        f'\n  — {status}'
    )
    await callback.message.unpin()
    
    try:
        await action(callback.message.chat.id, user_id)
    except TelegramBadRequest:
        ...
    
    try:
        await callback.bot.send_message(user_id, text_message)
    except TelegramForbiddenError:
        ...


async def _send_application(
        bot: Bot,
        user_id: int,
        user_name: str,
        message_ids: List[int],
        group_id: int,
        thread_id: Optional[int] = None
    ) -> Literal[0, 1]:
    try:
        await bot.forward_messages(group_id, user_id, message_ids, thread_id)
    except TelegramBadRequest:
        try:
            await bot.delete_messages(group_id, message_ids)
        except TelegramBadRequest:
            ...
        return 1
    else:
        application_message = await bot.send_message(
            group_id,
            f'✉️ Новая заявка на вступление от <i>{user_name}</i>',
            message_thread_id=thread_id,
            reply_markup=JoinRequestKeyboard.markup(user_id)
        )
        await application_message.pin()
        return 0
