from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import logging

logging.basicConfig(level=logging.INFO)


class VideoBot:
    def __init__(self, token, db, text_to_sql):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db = db
        self.text_to_sql = text_to_sql

        # Подключаем обработчики команд
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.handle_message)

    async def start_command(self, message: Message):
        await message.answer(
            "Привет! Я бот для статистики видео.\n\n"
            "Примеры вопросов:\n"
            "• Сколько всего видео?\n"
            "• Сколько видео у креатора с id aca1061a9d324ecf8c3fa2bb32d7be63?\n"
            "• Сколько видео набрало больше 1000 просмотров?\n"
            "• На сколько просмотров выросли видео 28 ноября 2025?\n"
            "• Сколько разных видео получали просмотры 27 ноября 2025?"
        )

    async def help_command(self, message: Message):
        await message.answer(
            "Просто напиши вопрос про видео.\n"
            "Я пойму даты, числа и id креаторов.\n"
            "Всегда отвечаю одним числом."
        )

    async def handle_message(self, message: Message):
        # Показываем что бот печатает
        await self.bot.send_chat_action(message.chat.id, action="typing")

        try:
            user_text = message.text
            print(f"Получил вопрос: {user_text}")

            # Превращаем текст в SQL
            sql = self.text_to_sql.to_sql(user_text)

            if not sql:
                await message.answer(
                    "Не понял вопрос. Попробуй переформулировать.\n"
                    "Примеры можно посмотреть в /help"
                )
                return

            print(f"SQL запрос: {sql}")

            # Пробуем получить одно число
            result = await self.db.fetch_one(sql)

            # Если не получилось, берем первую колонку из первой строки
            if result is None:
                rows = await self.db.fetch_all(sql)
                if rows and len(rows) > 0:
                    result = rows[0][0]
                else:
                    result = 0

            await message.answer(f"Ответ: {result}")

        except Exception as e:
            print(f"Ошибка: {e}")
            await message.answer("Что-то пошло не так. Попробуй позже.")

    async def start(self):
        await self.dp.start_polling(self.bot)