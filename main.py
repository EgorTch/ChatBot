# main.py
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from db import create_table
from handlers import router
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация объекта бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков команд
dp.include_router(router)

# Основной цикл
async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Приложение остановлено.')