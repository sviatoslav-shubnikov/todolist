from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select, Button, Row, Multiselect, Cancel

from config import API_URL
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import logging
from datetime import datetime
from aiogram.utils.markdown import hbold, hitalic

import json

logger = logging.getLogger(__name__)


dialog_router = Router()


async def get_user_tasks(user_id: int):

    try:
        async with aiohttp.ClientSession() as session:

            async with session.get(f"{API_URL}todolist/get_user_tasks/{user_id}/", headers={"Host": "localhost"}) as resp:

                if resp.status == 200:
                    response_data = await resp.json()

                    if response_data.get("status") == "success":
                        return response_data.get("data", [])
                    
                    return None
                
                return None
            
    except Exception as e:
        logger.exception(f"Ошибка при получении задач для пользователя {user_id}")
        return None

def format_due_date(due_date_str: str) -> str:

    try:
        dt = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return "не указан"

def format_created_at(created_at_str: str) -> str:

    try:
        dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return "не указано"
    

def format_categories(categories: list) -> str:

    if not categories:
        return ""
    return "🏷 Категории: " + ", ".join(categories)

    
@dialog_router.message(Command("tasks"))
async def cmd_tasks(message: types.Message):

    user_id = message.from_user.id
    tasks = await get_user_tasks(user_id)
    
    if tasks is None:
        await message.answer("Произошла ошибка при получении задач.")
        return
    
    if not tasks:
        await message.answer("У вас пока нет задач.")
        return
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Закрыть",
        callback_data="close_tasks"
    ))
    
    tasks_text = hbold("📋 Ваши задачи:\n\n")
    for task in tasks:
        status_emoji = {
            "pending": "🟡",
            "completed": "🟢",
            "overdue": "🔴"
        }.get(task.get("Status"), "⚪")

        due_date = format_due_date(task.get("DueDate"))
        created_at = format_created_at(task.get("CreatedAt"))
        categories_text = format_categories(task.get("Categories", []))

        task_entry = (
            f"\n{status_emoji} {hbold(task.get('Title', 'Без названия'))}\n"
            f"📝 {hitalic(task.get('Description', 'нет описания'))}\n"
            f"⏰ Дедлайн: {due_date}\n"
            f"📅 Создано: {created_at}\n"
        )

        if categories_text:
            task_entry += f"{categories_text}\n"

        tasks_text += task_entry

    await message.delete()
    await message.answer(tasks_text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )


@dialog_router.callback_query(lambda c: c.data == "close_tasks")
async def close_tasks(callback: types.CallbackQuery):

    await callback.message.delete()
    await callback.answer("Список задач закрыт")


@dialog_router.message(Command("today"))
async def cmd_today(message: types.Message):

    user_id = message.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_user_tasks_on_today/{user_id}",
                headers={"Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    if response_data.get("status") == "success":
                        tasks = response_data.get("data", [])
                        
                        if not tasks:
                            await message.answer("На сегодня у вас нет задач! 🎉")
                            return
                            
                        builder = InlineKeyboardBuilder()
                        builder.add(types.InlineKeyboardButton(
                            text="Закрыть",
                            callback_data="close_today_tasks"
                        ))
                        
                        tasks_text = hbold("📅 Ваши задачи на сегодня:\n\n")
                        for task in tasks:
                            status_emoji = {
                                "pending": "🟡",   
                                "completed": "🟢",  
                                "overdue": "🔴"     
                            }.get(task.get("Status"), "⚪")
                            due_date = format_due_date(task.get("DueDate"))
                            created_at = format_created_at(task.get("CreatedAt"))

                            categories_text = format_categories(task.get("Categories", []))
                            
                            task_entry = (
                                f"{status_emoji} {hbold(task.get('Title', 'Без названия'))}\n"
                                f"📝 {hitalic(task.get('Description', 'нет описания'))}\n"
                                f"⏰ Время: {due_date.split()[1] if due_date != 'не указан' else 'не указано'}\n"
                                f"📅 Создано: {created_at}\n"
                            )
                            
                            if categories_text:
                                task_entry += f"{categories_text}\n"
                                
                            tasks_text += task_entry
                        
                        await message.answer(
                            tasks_text,
                            reply_markup=builder.as_markup(),
                            parse_mode="HTML"
                        )
                        return
                    
                await message.answer("⚠️ Не удалось получить задачи на сегодня.")
                
    except Exception as e:
        logger.exception(f"Ошибка при получении задач на сегодня для пользователя {user_id}")
        await message.answer("🚫 Произошла ошибка при подключении к серверу.")


@dialog_router.callback_query(lambda c: c.data == "close_today_tasks")
async def close_today_tasks(callback: types.CallbackQuery):

    await callback.message.delete()
    await callback.answer("Список задач на сегодня закрыт")


class AddTaskSG(StatesGroup):

    title = State()
    description = State()
    due = State()
    category = State()
    confirm = State()


async def on_title(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["title"] = message.text
    await manager.switch_to(AddTaskSG.description)


async def on_description(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["description"] = message.text
    await manager.switch_to(AddTaskSG.due)


async def on_due(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["due"] = message.text
    user_id = manager.event.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:

            async with session.get(f"{API_URL}todolist/get_task_categories/{user_id}", headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:
                
                if resp.status == 200:

                    response_data = await resp.json()

                    if response_data.get("status") == "success":
                        categories = response_data.get("data", [])

                        if categories: 
                            manager.dialog_data["fetched_categories"] = categories
                            await manager.switch_to(AddTaskSG.category)
                            return

                    manager.dialog_data["category_id"] = None
                    await manager.switch_to(AddTaskSG.confirm)
                    return
                    
    except Exception as e:
        logger.exception("Ошибка при получении категорий")
        await message.answer("🚫 Ошибка при подключении к API.")
        manager.dialog_data["category_id"] = None
        await manager.switch_to(AddTaskSG.confirm)


async def get_categories(dialog_manager: DialogManager, **kwargs):

    cats = dialog_manager.dialog_data.get("fetched_categories", [])
    return {
        "categories": [
            (cat["Name"], str(cat["id"])) for cat in cats  
        ]
    }


async def on_category_selected(callback: types.CallbackQuery, widget: Multiselect, manager: DialogManager, item_id: str):

    selected_ids = widget.get_checked()
    
    if item_id == "no_cats":
        manager.dialog_data["category_ids"] = []
    else:
        manager.dialog_data["category_ids"] = selected_ids
    
    await manager.next()


async def on_category_chosen(callback: types.CallbackQuery, widget: Select, manager: DialogManager, item_id: str):

    if "category_ids" not in manager.dialog_data:
        manager.dialog_data["category_ids"] = []
    
    if item_id not in manager.dialog_data["category_ids"]:
        manager.dialog_data["category_ids"].append(item_id)

        await callback.answer(f"Добавлена категория: {item_id}")

    else:
        await callback.answer("Категория уже выбрана.")

async def finish_category_selection(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(AddTaskSG.confirm)


async def no_categories(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    manager.dialog_data["category_ids"] = []
    await manager.switch_to(AddTaskSG.confirm)



async def on_submit(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    data = manager.dialog_data
    task_payload = {
        "Title": data["title"],
        "Description": data.get("description", ""),
        "DueDate": data["due"],
        "TelegramId": callback.from_user.id,
    }

    if "category_ids" in data and data["category_ids"]:
        task_payload["Categories"] = data["category_ids"]
    

    try:
        async with aiohttp.ClientSession() as session:

            async with session.post(f"{API_URL}todolist/create_task/", json=task_payload, headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:

                response = await resp.json()
                logger.debug(f"Ответ API: {response}")  
                
                if resp.status in (200, 201):
                    await callback.message.answer("✅ Задача успешно добавлена!")
                else:
                    error_msg = response.get("message", "Unknown error")

                    await callback.message.answer(f"⚠️ Ошибка: {error_msg}")

    except Exception as e:
        logger.exception("Ошибка при создании задачи")
        await callback.message.answer("🚫 Ошибка подключения к API")

    await manager.done()


@dialog_router.message(Command("add"))
async def cmd_add(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(AddTaskSG.title)


dialog_add_task = Dialog(
    Window(
        Const("Введите название задачи:"),
        MessageInput(on_title),
        state=AddTaskSG.title,
    ),
    Window(
        Const("Введите описание задачи:"),
        MessageInput(on_description),
        state=AddTaskSG.description,
    ),
    Window(
        Const("Введите дедлайн (например: 2025-06-01 15:00):"),
        MessageInput(on_due),
        state=AddTaskSG.due,
    ),
    Window(
        Const("Выберите категории (можно несколько):"),
        Select(
            Format("🏷 {item[0]}"),
            id="cat_select",
            item_id_getter=lambda x: x[1],
            items="categories",
            on_click=on_category_chosen,
        ),
        Row(
            Button(Const("✅ Завершить выбор категорий"), id="finish_categories", on_click=finish_category_selection),
            Button(Const("⛔ Без категорий"), id="no_categories", on_click=no_categories),
        ),
        state=AddTaskSG.category,
        getter=get_categories,
    ),

    Window(
        Const("Подтвердите создание задачи."),
        Row(Button(Const("✅ Подтвердить"), id="confirm", on_click=on_submit)),
        state=AddTaskSG.confirm,
    )

)


dialog_router.include_router(dialog_add_task)


class EditTaskSG(StatesGroup):

    select_task = State()
    select_field = State()
    edit_title = State()
    edit_description = State()
    edit_due = State()
    edit_status = State()
    edit_categories = State()
    confirm = State()


async def get_tasks_for_edit(dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id
    tasks = await get_user_tasks(user_id)
    return {
        "tasks": [(f"{task['Title']}", task['id']) for task in tasks] if tasks else []
    }


async def on_task_selected(callback: types.CallbackQuery, _, manager: DialogManager, item_id: str):

    manager.dialog_data["task_id"] = item_id
    await manager.switch_to(EditTaskSG.select_field)


async def on_field_selected(callback: types.CallbackQuery, _, manager: DialogManager, item_id: str):

    manager.dialog_data["edit_field"] = item_id

    if item_id == "title":
        await manager.switch_to(EditTaskSG.edit_title)

    elif item_id == "description":
        await manager.switch_to(EditTaskSG.edit_description)

    elif item_id == "due":
        await manager.switch_to(EditTaskSG.edit_due)

    elif item_id == "status":
        await manager.switch_to(EditTaskSG.edit_status)

    elif item_id == "categories":
        await manager.switch_to(EditTaskSG.edit_categories)


async def on_edit_title(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["new_title"] = message.text
    await manager.switch_to(EditTaskSG.confirm)


async def on_edit_description(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["new_description"] = message.text
    await manager.switch_to(EditTaskSG.confirm)


async def on_edit_due(message: types.Message, _, manager: DialogManager):

    manager.dialog_data["new_due"] = message.text
    await manager.switch_to(EditTaskSG.confirm)


async def on_status_selected(callback: types.CallbackQuery, _, manager: DialogManager, item_id: str):

    manager.dialog_data["new_status"] = item_id
    await manager.switch_to(EditTaskSG.confirm)


async def get_categories_for_edit(dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(f"{API_URL}todolist/get_task_categories/{user_id}", headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:

                if resp.status == 200:
                    response_data = await resp.json()

                    if response_data.get("status") == "success":

                        cats = response_data.get("data", [])
                        return {"categories": [(c["Name"], c["id"]) for c in cats]}
                    
    except Exception as e:
        logger.exception("Ошибка при получении категорий")

    return {"categories": []}


async def fetch_task_data(task_id: str, user_id: int): 

    try:
        async with aiohttp.ClientSession() as session:

            async with session.get(f"{API_URL}todolist/get_user_task/{task_id}/{user_id}", headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:

                if resp.status == 200:
                    data = await resp.json()

                    return data.get("data", {})
                
    except Exception as e:
        logger.exception("Ошибка при получении данных задачи")
    
    return {}


async def skip_categories(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    manager.dialog_data["new_categories"] = []  
    await manager.switch_to(EditTaskSG.confirm)


async def on_category_chosen_edit(callback: types.CallbackQuery, widget: Select, manager: DialogManager, item_id: str):

    if "new_categories" not in manager.dialog_data:
        manager.dialog_data["new_categories"] = []

    if item_id not in manager.dialog_data["new_categories"]:
        manager.dialog_data["new_categories"].append(item_id)

        await callback.answer("✅ Категория добавлена")

    else:
        await callback.answer("⚠️ Уже выбрана")

async def finish_category_selection_edit(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    if "new_categories" not in manager.dialog_data:
        manager.dialog_data["new_categories"] = []

    await manager.switch_to(EditTaskSG.confirm)

async def skip_categories(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    
    manager.dialog_data["new_categories"] = []  
    await manager.switch_to(EditTaskSG.confirm)


async def on_edit_confirm(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    data = manager.dialog_data
    task_id = data["task_id"]
    user_id = callback.from_user.id

    current_task = await fetch_task_data(task_id, user_id)

    if not current_task:

        await callback.message.answer("⚠️ Не удалось загрузить текущие данные задачи.")
        return

    task_payload = {
        "id": task_id,
        "TelegramId": user_id,
        "Title": data.get("new_title", current_task.get("Title", "")),
        "Description": data.get("new_description", current_task.get("Description", "")),
        "DueDate": data.get("new_due", current_task.get("DueDate", "")),
        "Status": data.get("new_status", current_task.get("Status", "")),
    }


    if "new_categories" in data:
        task_payload["Categories"] = list(data["new_categories"])

    else:
        task_payload["Categories"] = current_task.get("Categories", [])

    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(f"{API_URL}todolist/edit_task/", json=task_payload, headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:
                
                if resp.status == 200:
                    await callback.message.answer("✅ Задача успешно обновлена!")
                
                else:
                    error_msg = await resp.text()
                    await callback.message.answer(f"⚠️ Не удалось обновить задачу. Код: {resp.status}. Ошибка: {error_msg}")

    except Exception as e:
        logger.exception("Ошибка при обновлении задачи")
        await callback.message.answer("🚫 Ошибка при подключении к API.")

    await manager.done()


dialog_edit_task = Dialog(
    Window(
        Const("Выберите задачу для редактирования:"),
        Select(
            text=Format("{item[0]}"),
            id="task_select",
            item_id_getter=lambda x: x[1],
            items="tasks",
            on_click=on_task_selected,
        ),
        state=EditTaskSG.select_task,
        getter=get_tasks_for_edit,
    ),
    Window(
        Const("Что вы хотите изменить?"),
        Select(
            text=Format("{item[0]}"),
            id="field_select",
            item_id_getter=lambda x: x[1],
            items=[
                ("Название", "title"),
                ("Описание", "description"),
                ("Дедлайн", "due"),
                ("Статус", "status"),
                ("Категории", "categories"),
            ],
            on_click=on_field_selected,
        ),
        state=EditTaskSG.select_field,
    ),
    Window(
        Const("Введите новое название задачи:"),
        MessageInput(on_edit_title),
        state=EditTaskSG.edit_title,
    ),
    Window(
        Const("Введите новое описание задачи:"),
        MessageInput(on_edit_description),
        state=EditTaskSG.edit_description,
    ),
    Window(
        Const("Введите новый дедлайн (например: 2025-06-01 15:00):"),
        MessageInput(on_edit_due),
        state=EditTaskSG.edit_due,
    ),
    Window(
        Const("Выберите новый статус:"),
        Select(
            text=Format("{item[0]}"),
            id="status_select",
            item_id_getter=lambda x: x[1],
            items=[
                ("В работе", "pending"),
                ("Завершено", "completed"),
                ("Просрочено", "overdue"),
            ],
            on_click=on_status_selected,
        ),
        state=EditTaskSG.edit_status,
    ),
    Window(
        Const("Выберите новые категории (по одной). Когда закончите — нажмите 'Завершить выбор':"),
        Select(
            Format("🏷 {item[0]}"),
            id="cat_select",
            item_id_getter=lambda x: x[1],
            items="categories",
            on_click=on_category_chosen_edit,
        ),
        Row(
            Button(Const("✅ Завершить выбор"), id="finish_categories_edit", on_click=finish_category_selection_edit),
            Button(Const("⛔ Пропустить"), id="skip_categories", on_click=skip_categories),
        ),
        state=EditTaskSG.edit_categories,
        getter=get_categories_for_edit,
    ),

    Window(
        Const("Подтвердите изменения:"),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_edit_confirm),
            Button(Const("❌ Отмена"), id="cancel", on_click=lambda c, b, m: m.done()),
        ),
        state=EditTaskSG.confirm,
    )
)

@dialog_router.message(Command("edit"))
async def cmd_edit(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(EditTaskSG.select_task)


dialog_router.include_router(dialog_edit_task)


class DeleteTaskSG(StatesGroup):

    select_task = State()
    confirm = State()


async def get_tasks_for_delete(dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id
    tasks = await get_user_tasks(user_id)
    return {
        "tasks": [(f"{task['Title']}", task['id']) for task in tasks] if tasks else []
    }


async def on_task_selected_for_delete(callback: types.CallbackQuery, _, manager: DialogManager, item_id: str):

    manager.dialog_data["task_id"] = item_id
    await manager.switch_to(DeleteTaskSG.confirm)


async def on_delete_confirm(callback: types.CallbackQuery, button: Button, manager: DialogManager):

    data = manager.dialog_data
    task_id = data["task_id"]
    user_id = callback.from_user.id

    try:
        async with aiohttp.ClientSession() as session:

            async with session.delete(f"{API_URL}todolist/delete_task/", json={"id": task_id, "TelegramId": user_id}, headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:
                
                if resp.status == 200:
                    await callback.message.answer("✅ Задача успешно удалена!")
                
                else:
                    response = await resp.json()
                    
                    await callback.message.answer(f"⚠️ Не удалось удалить задачу. Ошибка: {response.get('message', 'Unknown error')}")
    
    except Exception:
        logger.exception("Ошибка при удалении задачи")
        await callback.message.answer("🚫 Ошибка при подключении к API.")

    await manager.done()


dialog_delete_task = Dialog(
    Window(
        Const("Выберите задачу для удаления:"),
        Select(
            text=Format("{item[0]}"),
            id="task_select",
            item_id_getter=lambda x: x[1],
            items="tasks",
            on_click=on_task_selected_for_delete,
        ),
        state=DeleteTaskSG.select_task,
        getter=get_tasks_for_delete,
    ),
    Window(
        Const("Вы уверены, что хотите удалить эту задачу?"),
        Row(
            Button(Const("✅ Да, удалить"), id="confirm", on_click=on_delete_confirm),
            Button(Const("❌ Нет, отменить"), id="cancel", on_click=lambda c, b, m: m.done()),
        ),
        state=DeleteTaskSG.confirm,
    )
)


@dialog_router.message(Command("delete"))
async def cmd_delete(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DeleteTaskSG.select_task)


dialog_router.include_router(dialog_delete_task)