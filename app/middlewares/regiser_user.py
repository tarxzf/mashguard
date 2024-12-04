from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Any, Awaitable, Callable, Dict

from loader import database


class RegisteringUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Awaitable[Any]:
        if not message.from_user.is_bot:
            user_id = message.from_user.id

            row = await database.fetchone(
                'SELECT id FROM users WHERE id = %s;',
                (user_id,)
            )
            if row is None:
                await database.execute(
                    'INSERT INTO users(id) VALUES(%s);',
                    (user_id,)
                )
        
        result = await handler(message, data)
        return result
