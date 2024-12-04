from environs import Env
from typing import Optional

env = Env()
env.read_env()

# Телеграм токен бота
token = env.str('TOKEN')

# IP Адрес сервера с базой данных
host = env.str('HOST')

# Порт сервера с базой данных
port = env.int('PORT')

# Пользователь базы данных
user = env.str('DB_USER')

# Пароль пользователя базы данных
password = env.str('PASSWORD')

# Имя базы данных
database = env.str('DATABASE')

# Айди Телеграм-группы
group_id = env.int('GROUP_ID')

# Айди топика
message_thread_id = env.int('MESSAGE_THREAD_ID')

dsn = f'postgresql://{user}:{password}@{host}:{port}/{database}'

LOGGING_PATH = 'app/data/logs.log'

COMMANDS = {
    'start': 'Начать'
}