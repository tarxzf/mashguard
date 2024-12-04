import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from pathlib import Path

from data.config import token, dsn, LOGGING_PATH
from utils.database import Database

root_path = Path(__file__).parent.parent.absolute()

logger = logging.getLogger('main')
logging.basicConfig(
    filename=root_path / LOGGING_PATH,
    format='%(asctime)s | %(levelname)s - %(name)s: %(message)s',
    level=logging.INFO
)

default = DefaultBotProperties(parse_mode=ParseMode.HTML)

bot = Bot(
    token=token,
    default=default
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

database = Database(dsn)
