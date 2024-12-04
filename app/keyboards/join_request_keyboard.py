from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class JoinRequestKeyboard:
    button_callback_1 = 'join_request'

    button_text_2 = '✅ Принять'
    button_callback_2 = f'{button_callback_1} approve'

    button_text_3 = '🚫 Отклонить'
    button_callback_3 = f'{button_callback_1} decline'

    @classmethod
    def markup(self, user_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=self.button_text_2,
                        callback_data=f'{self.button_callback_2} {user_id}'
                    ),
                    InlineKeyboardButton(
                        text=self.button_text_3,
                        callback_data=f'{self.button_callback_3} {user_id}'
                    )
                ]
            ]
        )
