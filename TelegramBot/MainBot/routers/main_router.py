from aiogram import Router
from handlers import common
from dialogs.dialog_tasks import dialog_router
from dialogs.dialog_categories import category_router

main_router = Router()
main_router.include_router(common.router)

main_router.include_router(dialog_router)
main_router.include_router(category_router)