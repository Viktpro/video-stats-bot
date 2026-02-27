import re
from gigachat import GigaChat


class TextToSQL:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.use_gigachat = bool(api_key)

        self.months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }

        if self.use_gigachat:
            print("🤖 Используется GigaChat")
            self.giga = GigaChat(credentials=api_key, verify_ssl_certs=False)
            self.prompt = self._create_prompt()
        else:
            print("⚠️ GigaChat не используется, работаем в режиме парсинга")

    def _create_prompt(self):
        return """
Ты помощник, который преобразует вопросы на русском языке в SQL запросы.
Отвечай ТОЛЬКО SQL кодом, без пояснений.

Таблицы в базе данных:

1. videos - информация о видео
   - id (TEXT) - идентификатор видео
   - creator_id (TEXT) - идентификатор создателя видео
   - video_created_at (TIMESTAMP) - дата и время публикации
   - views_count (INTEGER) - общее количество просмотров
   - likes_count (INTEGER) - общее количество лайков
   - comments_count (INTEGER) - общее количество комментариев
   - reports_count (INTEGER) - общее количество жалоб

2. video_snapshots - почасовые снимки статистики
   - video_id (TEXT) - ссылка на видео
   - created_at (TIMESTAMP) - время замера (каждый час)
   - views_count (INTEGER) - просмотры на момент замера
   - likes_count (INTEGER) - лайки на момент замера
   - comments_count (INTEGER) - комментарии на момент замера
   - reports_count (INTEGER) - жалобы на момент замера
   - delta_views_count (INTEGER) - прирост просмотров за час
   - delta_likes_count (INTEGER) - прирост лайков за час
   - delta_comments_count (INTEGER) - прирост комментариев за час
   - delta_reports_count (INTEGER) - прирост жалоб за час

ПРИМЕРЫ ЗАПРОСОВ:

1. "Сколько всего видео?"
   SELECT COUNT(*) FROM videos

2. "Какое общее количество лайков набрали все видео?"
   SELECT SUM(likes_count) FROM videos

3. "Какое общее количество просмотров набрали все видео?"
   SELECT SUM(views_count) FROM videos

4. "Сколько видео у креатора с id 123 вышло с 1 ноября 2025 по 5 ноября 2025?"
   SELECT COUNT(*) FROM videos 
   WHERE creator_id = '123' 
   AND DATE(video_created_at) BETWEEN '2025-11-01' AND '2025-11-05'

5. "Сколько видео набрало больше 1000 просмотров?"
   SELECT COUNT(*) FROM videos WHERE views_count > 1000

6. "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
   SELECT COALESCE(SUM(delta_views_count), 0) 
   FROM video_snapshots 
   WHERE DATE(created_at) = '2025-11-28'

7. "Сколько разных видео получали новые просмотры 27 ноября 2025?"
   SELECT COUNT(DISTINCT video_id) 
   FROM video_snapshots 
   WHERE DATE(created_at) = '2025-11-27' 
   AND delta_views_count > 0

ПРАВИЛА ПРЕОБРАЗОВАНИЯ ДАТ:
- "28 ноября 2025" → '2025-11-28'
- "с 1 по 5 ноября 2025" → BETWEEN '2025-11-01' AND '2025-11-05'
- "29 января 2025" → '2025-01-29'
- ID креаторов всегда в кавычках: '123'
"""

    def _parse_manually(self, text):
        text = text.lower().strip()

        # 1. Сколько всего видео?
        if "сколько всего видео" in text:
            return "SELECT COUNT(*) FROM videos"

        # 2. Общее количество лайков
        if "общее количество лайков" in text or "сколько лайков" in text:
            return "SELECT SUM(likes_count) FROM videos"

        # 3. Общее количество просмотров
        if "общее количество просмотров" in text or "сколько просмотров" in text:
            return "SELECT SUM(views_count) FROM videos"

        # 4. Креатор по id
        creator_match = re.search(r'креатора с id[^\d]*([a-f0-9]+)', text)
        if creator_match:
            creator_id = creator_match.group(1)
            return f"SELECT COUNT(*) FROM videos WHERE creator_id = '{creator_id}'"

        # 5. Больше N просмотров
        views_match = re.search(r'больше[^\d]*(\d+)', text)
        if views_match and 'просмотров' in text:
            views = views_match.group(1)
            return f"SELECT COUNT(*) FROM videos WHERE views_count > {views}"

        # 6. Поиск даты
        date_match = re.search(r'(\d{1,2})\s+([а-я]+)\s+(\d{4})', text)
        if date_match:
            day = date_match.group(1)
            month_name = date_match.group(2)
            year = date_match.group(3)

            if month_name in self.months:
                month = self.months[month_name]
                date_str = f"{year}-{month:02d}-{int(day):02d}"

                if 'выросли' in text or 'прирост' in text:
                    return f"""
                        SELECT COALESCE(SUM(delta_views_count), 0)
                        FROM video_snapshots
                        WHERE DATE(created_at) = '{date_str}'
                    """

                if 'разных видео' in text:
                    return f"""
                        SELECT COUNT(DISTINCT video_id)
                        FROM video_snapshots
                        WHERE DATE(created_at) = '{date_str}'
                        AND delta_views_count > 0
                    """

        # 7. Поиск периода
        period_match = re.search(r'с\s+(\d{1,2})\s+по\s+(\d{1,2})\s+([а-я]+)\s+(\d{4})', text)
        if period_match:
            start = period_match.group(1)
            end = period_match.group(2)
            month_name = period_match.group(3)
            year = period_match.group(4)

            if month_name in self.months:
                month = self.months[month_name]
                creator_match = re.search(r'креатора с id[^\d]*([a-f0-9]+)', text)
                if creator_match:
                    creator_id = creator_match.group(1)
                    return f"""
                        SELECT COUNT(*)
                        FROM videos
                        WHERE creator_id = '{creator_id}'
                        AND DATE(video_created_at) BETWEEN '{year}-{month:02d}-{int(start):02d}' AND '{year}-{month:02d}-{int(end):02d}'
                    """

        return None

    def convert(self, text):
        if self.use_gigachat:
            try:
                print(f"Отправляю в GigaChat: {text}")

                response = self.giga.chat({
                    "messages": [
                        {"role": "system", "content": self.prompt},
                        {"role": "user", "content": f"Вопрос: {text}\nSQL:"}
                    ]
                })

                sql = response['choices'][0]['message']['content']
                sql = sql.replace('```sql', '').replace('```', '').strip()
                print(f"✅ GigaChat ответил: {sql}")
                return sql

            except Exception as e:
                print(f"❌ Ошибка GigaChat: {e}")
                print("🔄 Использую запасной парсинг")
                return self._parse_manually(text)
        else:
            return self._parse_manually(text)


text_to_sql = None