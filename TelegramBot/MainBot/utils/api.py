import aiohttp
import logging
from config import API_URL 

logger = logging.getLogger(__name__)

async def create_user(telegram_id: int):
    url = f"{API_URL}todolist/create_user/"
    payload = {"TelegramId": telegram_id}
	
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers={'Content-Type': 'application/json', "Host": "localhost"}) as resp:
                if resp.status == 200:
                    logger.info(f"✅ User {telegram_id} registered")
                else:
                    error = await resp.text()
                    logger.warning(f"⚠️ Failed to register {telegram_id}: {resp.status}, {error}")
        except Exception as e:
            logger.exception(f"❌ Exception during user creation: {e}")
