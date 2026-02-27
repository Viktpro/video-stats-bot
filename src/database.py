import asyncpg
import json
from datetime import datetime


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        from src.config import config
        self.pool = await asyncpg.create_pool(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password
        )
        print("Подключились к базе данных")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("Отключились от базы данных")

    async def fetch_one(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    def _parse_date(self, date_str):
        """Превращает строку с датой в объект datetime"""
        if 'Z' in date_str:
            date_str = date_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=None)

    async def load_data(self, file_path):
        """Загружает данные из JSON файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        videos = data.get('videos', [])
        print(f"Нашли {len(videos)} видео в файле")

        async with self.pool.acquire() as conn:
            for item in videos:
                # Вставляем видео
                created_at = self._parse_date(item['video_created_at'])
                await conn.execute("""
                    INSERT INTO videos (id, creator_id, video_created_at, views_count,
                                      likes_count, comments_count, reports_count)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (id) DO NOTHING
                """, item['id'], item['creator_id'], created_at,
                                   item['views_count'], item['likes_count'],
                                   item['comments_count'], item['reports_count'])

                # Вставляем снапшоты
                snapshots = item.get('snapshots', [])
                for snap in snapshots:
                    snap_time = self._parse_date(snap['created_at'])
                    await conn.execute("""
                        INSERT INTO video_snapshots
                        (video_id, views_count, likes_count, comments_count, reports_count,
                         delta_views_count, delta_likes_count, delta_comments_count,
                         delta_reports_count, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        ON CONFLICT (video_id, created_at) DO NOTHING
                    """, snap['video_id'], snap['views_count'], snap['likes_count'],
                                       snap['comments_count'], snap['reports_count'],
                                       snap['delta_views_count'], snap['delta_likes_count'],
                                       snap['delta_comments_count'], snap['delta_reports_count'],
                                       snap_time)

        print(f"Загрузили {len(videos)} видео в базу")


# Создаем один экземпляр на всё приложение
db = Database()