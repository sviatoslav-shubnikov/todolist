from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Select, Cancel, Back
from config import API_URL
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


category_router = Router()

class ListCategoriesSG(StatesGroup):
    view_categories = State()

def format_category_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return "не указано"

async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_task_categories/{user_id}",
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    if response.get("status") == "success":
                        categories = []
                        for cat in response.get("data", []):
                            categories.append({
                                "name": cat["Name"],
                                "id": cat["id"],
                                "created": format_category_date(cat["CreatedAt"]),
                            })
                        return {
                            "categories": categories,
                            "categories_text": await format_categories_text(categories)
                        }
    except Exception as e:
        logger.exception("Error fetching categories list")
    return {
        "categories": [],
        "categories_text": "У вас пока нет категорий."
    }

async def format_categories_text(categories: list) -> str:
    if not categories:
        return "У вас пока нет категорий."
    
    text = "📂 Ваши категории:\n\n"
    for i, cat in enumerate(categories, 1):
        text += (
            f"{i}. <b>{cat['name']}</b>\n"
            f"   🗓 Создано: {cat['created']}\n"
        )
    return text


    
@category_router.message(Command("categories"))
async def cmd_list_categories(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(ListCategoriesSG.view_categories)

dialog_list_categories = Dialog(
    Window(
        Format("{categories_text}"),
        state=ListCategoriesSG.view_categories,
        getter=get_user_categories,
    )
)


category_router.include_router(dialog_list_categories)


class CreateCategorySG(StatesGroup):
    name = State()
    confirm = State()

async def on_category_name(message: types.Message, _, manager: DialogManager):
    manager.dialog_data["name"] = message.text
    await manager.switch_to(CreateCategorySG.confirm)

async def on_category_confirm(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    data = manager.dialog_data
    category_payload = {
        "Name": data["name"],
        "TelegramId": callback.from_user.id
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}todolist/create_task_category/",
                json=category_payload,
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status in (200, 201):
                    response_data = await resp.json()
                    if response_data.get("status") == "success":
                        await callback.message.answer("✅ Категория успешно создана!")
                    else:
                        await callback.message.answer(f"⚠️ Ошибка при создании категории: {response_data.get('message')}")
                else:
                    await callback.message.answer(f"⚠️ Не удалось создать категорию. Код: {resp.status}")
    except Exception as e:
        logger.exception("Ошибка при создании категории")
        await callback.message.answer("🚫 Ошибка при подключении к API.")

    await manager.done()

@category_router.message(Command("create_category"))
async def cmd_create_category(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(CreateCategorySG.name)

dialog_create_category = Dialog(
    Window(
        Const("Введите название новой категории:"),
        MessageInput(on_category_name),
        state=CreateCategorySG.name,
    ),
    Window(
        Const("Подтвердите создание категории."),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_category_confirm),
            Button(Const("❌ Отмена"), id="cancel", on_click=lambda c, b, m: m.done()),
        ),
        state=CreateCategorySG.confirm,
    )
)


category_router.include_router(dialog_create_category)


class EditCategorySG(StatesGroup):
    select_category = State()
    edit_name = State()
    confirm = State()

async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_task_categories/{user_id}",
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    if response.get("status") == "success":
                        return {
                            "categories": [
                                (cat["Name"], cat["id"]) for cat in response.get("data", [])
                            ]
                        }
    except Exception as e:
        logger.exception("Error fetching categories")
    return {"categories": []}

async def on_category_selected(callback: types.CallbackQuery, widget: Select, 
                             manager: DialogManager, item_id: str):
    manager.dialog_data["category_id"] = item_id
    

    user_id = callback.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_task_category/{item_id}/{user_id}",
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    if response.get("status") == "success":
                        manager.dialog_data["current_name"] = response["data"]["Name"]
    except Exception as e:
        logger.exception("Error fetching category details")
    
    await manager.switch_to(EditCategorySG.edit_name)

async def on_name_entered(message: types.Message, widget: MessageInput, 
                         manager: DialogManager):
    manager.dialog_data["new_name"] = message.text
    await manager.switch_to(EditCategorySG.confirm)

async def on_confirm(callback: types.CallbackQuery, button: Button, 
                    manager: DialogManager):
    data = manager.dialog_data
    user_id = callback.from_user.id
    
    payload = {
        "id": data["category_id"],
        "TelegramId": user_id,
        "Name": data["new_name"]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{API_URL}todolist/edit_task_category/",
                json=payload,
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    await callback.message.answer("✅ Категория успешно обновлена!")
                else:
                    error = await resp.json()
                    await callback.message.answer(f"⚠️ Ошибка: {error.get('message', 'Unknown error')}")
    except Exception as e:
        logger.exception("Error updating category")
        await callback.message.answer("🚫 Ошибка подключения к серверу")
    
    await manager.done()

@category_router.message(Command("edit_category"))
async def cmd_edit_category(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(EditCategorySG.select_category)

dialog_edit_category = Dialog(
    Window(
        Const("Выберите категорию для редактирования:"),
        Select(
            Format("{item[0]}"),
            id="cat_select",
            item_id_getter=lambda x: x[1],
            items="categories",
            on_click=on_category_selected,
        ),
        Cancel(Const("❌ Отмена")),
        state=EditCategorySG.select_category,
        getter=get_user_categories,
    ),
    Window(
        Format("Текущее название: {dialog_data[current_name]}\n\nВведите новое название:"),
        MessageInput(on_name_entered),
        Back(Const("⬅️ Назад")),
        state=EditCategorySG.edit_name,
    ),
    Window(
        Const("Подтвердите изменение:"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=on_confirm),
        Back(Const("⬅️ Назад")),
        state=EditCategorySG.confirm,
    )
)

category_router.include_router(dialog_edit_category)


class DeleteCategorySG(StatesGroup):
    select_category = State()
    confirm = State()

async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_task_categories/{user_id}",
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    if response.get("status") == "success":
                        return {
                            "categories": [
                                (cat["Name"], cat["id"]) for cat in response.get("data", [])
                            ]
                        }
    except Exception as e:
        logger.exception("Error fetching categories for deletion")
    return {"categories": []}

async def on_category_selected(callback: types.CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    manager.dialog_data["category_id"] = item_id
    

    user_id = callback.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}todolist/get_task_category/{item_id}/{user_id}",
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    if response.get("status") == "success":
                        manager.dialog_data["category_name"] = response["data"]["Name"]
    except Exception as e:
        logger.exception("Error fetching category details for deletion")
    
    await manager.switch_to(DeleteCategorySG.confirm)


async def on_confirm_delete(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    data = manager.dialog_data
    user_id = callback.from_user.id
    
    payload = {
        "id": data["category_id"],
        "TelegramId": user_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{API_URL}todolist/delete_task_category/",
                json=payload,
                headers={'Content-Type': 'application/json', "Host": "localhost"}
            ) as resp:
                if resp.status == 200:
                    await callback.message.answer("✅ Категория успешно удалена!")
                else:
                    error = await resp.json()
                    await callback.message.answer(f"⚠️ Ошибка: {error.get('message', 'Unknown error')}")
    except Exception as e:
        logger.exception("Error deleting category")
        await callback.message.answer("🚫 Ошибка подключения к серверу")
    
    await manager.done()

@category_router.message(Command("delete_category"))
async def cmd_delete_category(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DeleteCategorySG.select_category)

dialog_delete_category = Dialog(
    Window(
        Const("Выберите категорию для удаления:"),
        Select(
            Format("{item[0]}"),
            id="cat_select",
            item_id_getter=lambda x: x[1],
            items="categories",
            on_click=on_category_selected,
        ),
        Cancel(Const("❌ Отмена")),
        state=DeleteCategorySG.select_category,
        getter=get_user_categories,
    ),
    Window(
        Format("Вы уверены, что хотите удалить категорию:\n\n<b>{dialog_data[category_name]}</b>?"),
        Button(Const("✅ Да, удалить"), id="confirm", on_click=on_confirm_delete),
        Back(Const("⬅️ Назад")),
        state=DeleteCategorySG.confirm,
    )
)


    

category_router.include_router(dialog_delete_category)
