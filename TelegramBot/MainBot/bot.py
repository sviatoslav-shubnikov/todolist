import os
import sys
import django

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from aiogram.types import BotCommand
from utils.logging_setup import setup_logging

from routers.main_router import main_router
from aiogram_dialog import setup_dialogs
from dialogs import dialog_tasks

async def main():
    setup_logging()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)

    await setup_bot_commands(bot)
    setup_dialogs(dp)

    await dp.start_polling(bot)

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="help", description="Помощь по командам"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="task", description="Посмотреть задачи"),
        BotCommand(command="today", description="Задачи на сегодня"),
        BotCommand(command="edit", description="Редактировать задачу"),
        BotCommand(command="delete", description="Удалить задачу"),
        BotCommand(command="categories", description="Категории"),
        BotCommand(command="create_category", description="Создать категорию"),
        BotCommand(command="edit_category", description="Редактировать категорию"),
        BotCommand(command="delete_category", description="Удалить категорию"),
    ]
    await bot.set_my_commands(commands)

if __name__ == "__main__":
    asyncio.run(main())
