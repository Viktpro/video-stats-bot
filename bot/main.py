import asyncio
import logging
from aiogram import Bot, Dispatcher
from .config import Config
from .handlers import router
from .db import db

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await db.connect()
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
