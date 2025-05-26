import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_MAIN_BOT_TOKEN')
API_URL = os.getenv("TODO_API_URL")