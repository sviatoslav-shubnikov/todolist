from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold, hitalic
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog import DialogManager

from utils.api import create_user
from dialogs.dialog_categories import ListCategoriesSG
from dialogs.dialog_tasks import cmd_tasks, cmd_today, cmd_add, close_tasks, close_today_tasks

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить задачу")],
        [KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="📅 Сегодня")],
        [KeyboardButton(text="📂 Категории")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

router = Router()


@router.message(lambda message: message.text == "➕ Добавить задачу")
async def button_add_task(message: Message, dialog_manager: DialogManager):
    await cmd_add(message, dialog_manager)

@router.message(lambda message: message.text == "📋 Мои задачи")
async def button_show_tasks(message: Message):
    await cmd_tasks(message)

@router.message(lambda message: message.text == "📅 Сегодня")
async def button_show_today_tasks(message: Message):
    await cmd_today(message)

@router.message(lambda message: message.text == "📂 Категории")
async def open_categories_from_button(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ListCategoriesSG.view_categories)


@router.callback_query(lambda c: c.data == "close_tasks")
async def handle_close_tasks(callback: CallbackQuery):
    await close_tasks(callback)

@router.callback_query(lambda c: c.data == "close_today_tasks")
async def handle_close_today_tasks(callback: CallbackQuery):
    await close_today_tasks(callback)

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandStart):
    telegram_id = message.from_user.id
    await create_user(telegram_id)

    text = (
        f"{hbold('Добро пожаловать!')}\n\n"
        "Этот бот поможет вам управлять личными задачами 📝\n\n"
        f"Вы можете:\n"
        f"🔹 Добавлять задачи\n"
        f"🔹 Устанавливать дедлайны\n"
        f"🔹 Привязывать задачи к категориям\n"
        f"🔹 Получать напоминания о дедлайне\n\n"
        f"Начните с команды /add чтобы создать новую задачу либо /tasks чтобы увидеть список задач"
    )

    await message.answer(text, reply_markup=main_menu_keyboard)
    await message.delete()

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        f"{hbold('Справка по командам')}\n\n"
        f"{hbold('📌 Задачи:')}\n"
        f"/add — добавить новую задачу\n"
        f"/tasks — список всех задач\n"
        f"/today — задачи на сегодня\n"
        f"/edit — редактировать задачу\n"
        f"/delete — удалить задачу\n\n"
        f"{hbold('📂 Категории:')}\n"
        f"/categories — список категорий\n"
        f"/create_category — создать категорию\n"
        f"/edit_category — редактировать категорию\n"
        f"/delete_category — удалить категорию\n"
    )

    await message.answer(text, reply_markup=main_menu_keyboard)
