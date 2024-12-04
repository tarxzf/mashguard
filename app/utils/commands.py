from aiogram import Bot
from aiogram.types import BotCommand
from typing import Dict


async def set_commands(bot: Bot, commands: Dict[str, str]):
    _commands = [BotCommand(command=i[0], description=i[1]) for i in commands.items()]
    await bot.set_my_commands(_commands)
