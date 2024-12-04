from asyncio import run

from data.config import COMMANDS
from handlers import start_handler, join_request_handler, system_handler
from loader import bot, dp, database
from middlewares.regiser_user import RegisteringUserMiddleware
from utils.commands import set_commands


@dp.shutdown()
async def on_shutdown():
    await database.close()
    print('[*] Telegram-Bot closed')


async def main():
    await database.initialize()

    await database.execute(
        '''CREATE TABLE IF NOT EXISTS users(
            id BIGINT PRIMARY KEY NOT NULL,
            already_sent BOOLEAN DEFAULT false
        );
        '''
    )

    dp.include_routers(
        join_request_handler.router,
        system_handler.router,
        start_handler.router
    )
    dp.message.middleware(RegisteringUserMiddleware())

    await set_commands(bot, COMMANDS)

    print('[*] Telegram-Bot has been launched successfully!')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        run(main())
    except KeyboardInterrupt:
        ...
