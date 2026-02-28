import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def test():
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'video_stats'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )

        # Проверим таблицы
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print("Таблицы в базе:", [t['table_name'] for t in tables])

        # Проверим количество видео
        count = await conn.fetchval("SELECT COUNT(*) FROM videos")
        print(f"Количество видео: {count}")

        # Проверим сумму лайков
        likes = await conn.fetchval("SELECT SUM(likes_count) FROM videos")
        print(f"Сумма лайков: {likes}")

        await conn.close()
        print("✅ Все проверки пройдены!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


asyncio.run(test())