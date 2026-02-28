from aiogram import Router, types
from aiogram.filters import Command
from .db import db
from .simple_llm import SimpleLLM
import logging

router = Router()
llm = SimpleLLM()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "👋 Привет! Я бот для анализа статистики видео.\n\n"
        "Задай мне вопрос на русском языке, например:\n"
        "• Сколько всего видео в системе?\n"
        "• Сколько видео у креатора с id 123 вышло с 1 ноября 2025 по 5 ноября 2025?\n"
        "• Сколько видео набрало больше 100000 просмотров?\n"
        "• На сколько просмотров в сумме выросли все видео 28 ноября 2025?\n"
        "• Сколько разных видео получали новые просмотры 27 ноября 2025?"
    )

@router.message()
async def handle_query(message: types.Message):
    try:
        await message.bot.send_chat_action(message.chat.id, action="typing")
        
        sql_query = await llm.text_to_sql(message.text)
        logging.info(f"Generated SQL: {sql_query}")
        
        result = await db.execute_query(sql_query)
        
        if result and len(result) > 0:
            value = result[0][0]
            if value is None:
                value = 0
            await message.reply(str(value))
        else:
            await message.reply("0")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("Извините, произошла ошибка при обработке запроса.")
