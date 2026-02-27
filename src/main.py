import asyncio
import os

from src.config import config
from src.database import db
from src.llm_handler import TextToSQL
from src.bot import VideoBot


async def main():
    print("Запускаем бота...")

    # Проверяем есть ли токен бота
    if not config.bot_token:
        print("Ошибка: в файле .env нет BOT_TOKEN")
        return

    # Создаем обработчик текста (передаем ключ гигачата)
    text_to_sql = TextToSQL(api_key=config.gigachat_key)

    # Подключаемся к базе
    await db.connect()

    # Смотрим есть ли данные в базе
    videos_count = await db.fetch_one("SELECT COUNT(*) FROM videos")

    if videos_count == 0:
        # База пустая, нужно загрузить данные из json
        json_path = "data/videos.json"
        if os.path.exists(json_path):
            print("Загружаем данные...")
            await db.load_data(json_path)
            new_count = await db.fetch_one("SELECT COUNT(*) FROM videos")
            print(f"Загружено {new_count} видео")
        else:
            print(f"Файл {json_path} не найден. Положите его в папку data/")
    else:
        print(f"В базе уже есть {videos_count} видео")

    # Создаем и запускаем бота
    bot = VideoBot(token=config.bot_token, db=db, text_to_sql=text_to_sql)

    try:
        print("Бот запущен, можно писать ему в Telegram")
        await bot.start()
    except KeyboardInterrupt:
        print("Бот остановлен")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())