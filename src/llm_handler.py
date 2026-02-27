import re
from gigachat import GigaChat


class TextToSQL:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Если ключ есть - используем гигачат, если нет - парсим сами
        if api_key:
            print("Будем использовать GigaChat для понимания вопросов")
            self.giga = GigaChat(credentials=api_key, verify_ssl_certs=False)
            self.use_gigachat = True
        else:
            print("Ключ GigaChat не найден, будем разбирать запросы вручную")
            self.use_gigachat = False

    def _make_prompt(self):
        # Текст, который объясняет гигачату как устроена база
        return """
Ты помогаешь превращать вопросы на русском в SQL запросы.
Отвечай только SQL кодом, ничего лишнего не пиши.

У нас есть две таблицы:

1. videos - тут хранятся видео
   - id - айди видео
   - creator_id - айди автора
   - video_created_at - когда выложили видео
   - views_count - сколько просмотров всего
   - likes_count - сколько лайков всего
   - comments_count - сколько комментариев
   - reports_count - сколько жалоб

2. video_snapshots - снимки статистики каждый час
   - video_id - айди видео
   - created_at - когда сделали снимок
   - views_count - просмотров на тот момент
   - likes_count - лайков на тот момент
   - comments_count - комментариев на тот момент
   - reports_count - жалоб на тот момент
   - delta_views_count - на сколько просмотров выросло за час
   - delta_likes_count - на сколько лайков выросло за час
   - delta_comments_count - на сколько комментариев выросло за час
   - delta_reports_count - на сколько жалоб выросло за час

Примеры запросов:

1. "Сколько всего видео?"
   SELECT COUNT(*) FROM videos

2. "Сколько видео у креатора с id 123 вышло с 1 по 5 ноября 2025?"
   SELECT COUNT(*) FROM videos 
   WHERE creator_id = '123' 
   AND date(video_created_at) BETWEEN '2025-11-01' AND '2025-11-05'

3. "Сколько видео набрало больше 1000 просмотров?"
   SELECT COUNT(*) FROM videos WHERE views_count > 1000

4. "На сколько просмотров выросли все видео 28 ноября 2025?"
   SELECT coalesce(sum(delta_views_count), 0) 
   FROM video_snapshots 
   WHERE date(created_at) = '2025-11-28'

5. "Сколько разных видео получали новые просмотры 27 ноября 2025?"
   SELECT count(distinct video_id) 
   FROM video_snapshots 
   WHERE date(created_at) = '2025-11-27' 
   AND delta_views_count > 0

Про даты:
- "28 ноября 2025" -> '2025-11-28'
- "с 1 по 5 ноября 2025" -> between '2025-11-01' and '2025-11-05'
- "29 января 2025" -> '2025-01-29'
"""

    def _parse_manually(self, text):
        # Если гигачат не работает или нет ключа, парсим сами
        text = text.lower().strip()

        # Сколько всего видео
        if "сколько всего видео" in text:
            return "SELECT COUNT(*) FROM videos"

        # Поиск id креатора
        import re
        creator_match = re.search(r'креатора с id[^\d]*([a-f0-9]+)', text)
        if creator_match:
            creator_id = creator_match.group(1)
            return f"SELECT COUNT(*) FROM videos WHERE creator_id = '{creator_id}'"

        # Поиск числа просмотров
        views_match = re.search(r'больше[^\d]*(\d+)', text)
        if views_match and 'просмотров' in text:
            views = views_match.group(1)
            return f"SELECT COUNT(*) FROM videos WHERE views_count > {views}"

        # Поиск даты
        months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }

        # Ищем дату типа "28 ноября 2025"
        date_match = re.search(r'(\d{1,2})\s+([а-я]+)\s+(\d{4})', text)
        if date_match:
            day = date_match.group(1)
            month_name = date_match.group(2)
            year = date_match.group(3)

            if month_name in months:
                month = months[month_name]

                # Вопрос про прирост просмотров
                if 'выросли' in text or 'прирост' in text:
                    return f"""
                        SELECT coalesce(sum(delta_views_count), 0)
                        FROM video_snapshots
                        WHERE date(created_at) = '{year}-{month:02d}-{int(day):02d}'
                    """

                # Вопрос про разные видео
                if 'разных видео' in text:
                    return f"""
                        SELECT count(distinct video_id)
                        FROM video_snapshots
                        WHERE date(created_at) = '{year}-{month:02d}-{int(day):02d}'
                        AND delta_views_count > 0
                    """

        return None

    def to_sql(self, user_text):
        # Превращаем текст в SQL запрос
        if self.use_gigachat:
            try:
                print(f"Спрашиваем GigaChat: {user_text}")

                # Отправляем запрос в гигачат
                response = self.giga.chat({
                    "messages": [
                        {"role": "system", "content": self._make_prompt()},
                        {"role": "user", "content": f"Вопрос: {user_text}\nSQL:"}
                    ]
                })

                # Забираем ответ
                sql = response['choices'][0]['message']['content']
                # Чистим от markdown если есть
                sql = sql.replace('```sql', '').replace('```', '').strip()
                print(f"GigaChat ответил: {sql}")
                return sql

            except Exception as e:
                print(f"Ошибка с GigaChat: {e}")
                print("Пробуем распарсить вручную")
                return self._parse_manually(user_text)
        else:
            return self._parse_manually(user_text)
