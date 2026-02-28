import re


class SimpleLLM:
    async def text_to_sql(self, user_query: str) -> str:
        query = user_query.lower()

        # Словарь месяцев (падежи)
        months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
            'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
            'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12,
            'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4,
            'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12
        }

        # Функция для извлечения месяца и года из запроса
        def extract_month_year(text):
            for month_name, month_num in months.items():
                if month_name in text:
                    # Ищем год (2024, 2025, 2026 и т.д.)
                    year_match = re.search(r'20\d{2}', text)
                    if year_match:
                        return month_num, year_match.group(0)
            return None, None

        # 1. Сколько всего видео
        if "сколько всего видео" in query:
            return "SELECT COUNT(*) FROM videos;"

        # 2. Общее количество лайков
        if "общее количество лайков" in query or "сумму лайков" in query or "всего лайков" in query:
            return "SELECT COALESCE(SUM(likes_count), 0) FROM videos;"

        # 3. Суммарное количество просмотров за месяц
        if ("суммарное количество просмотров" in query or "просмотров набрали" in query) and (
                "опубликованные" in query or "вышли" in query):
            month_num, year = extract_month_year(query)
            if month_num and year:
                return f"""
                    SELECT COALESCE(SUM(views_count), 0) FROM videos 
                    WHERE EXTRACT(MONTH FROM video_created_at) = {month_num}
                    AND EXTRACT(YEAR FROM video_created_at) = {year};
                """

        # 4. Количество видео за месяц
        if ("сколько видео" in query or "видео появилось" in query) and (
                "опубликовано" in query or "вышло" in query or "появилось" in query):
            month_num, year = extract_month_year(query)
            if month_num and year:
                return f"""
                    SELECT COUNT(*) FROM videos 
                    WHERE EXTRACT(MONTH FROM video_created_at) = {month_num}
                    AND EXTRACT(YEAR FROM video_created_at) = {year};
                """

        # 5. Видео у креатора с UUID
        creator_uuid_match = re.search(r'креатора с id ([a-f0-9]{32})', query)
        if creator_uuid_match:
            creator_id = creator_uuid_match.group(1)

            # Поиск количества просмотров
            views_match = re.search(r'больше ([\d\s]+) просмотров', query)
            if views_match:
                views = views_match.group(1).replace(' ', '')
                return f"""
                    SELECT COUNT(*) FROM videos 
                    WHERE creator_id = '{creator_id}'
                    AND views_count > {views};
                """
            return f"SELECT COUNT(*) FROM videos WHERE creator_id = '{creator_id}';"

        # 6. Видео у креатора с числовым ID
        creator_num_match = re.search(r'креатора с id (\d+)', query)
        if creator_num_match:
            creator_id = creator_num_match.group(1)

            # Поиск дат в формате "с 1 ноября 2025 по 5 ноября 2025"
            date_range = re.search(r'с (\d+) (\w+) (\d+) по (\d+) (\w+) (\d+)', query)
            if date_range:
                day1, month1, year1, day2, month2, year2 = date_range.groups()
                month1_num = months.get(month1.lower(), 1)
                month2_num = months.get(month2.lower(), 1)
                return f"""
                    SELECT COUNT(*) FROM videos 
                    WHERE creator_id = {creator_id} 
                    AND video_created_at >= '{year1}-{month1_num:02d}-{int(day1):02d}'
                    AND video_created_at <= '{year2}-{month2_num:02d}-{int(day2):02d} 23:59:59';
                """

            # Поиск количества просмотров
            views_match = re.search(r'больше ([\d\s]+) просмотров', query)
            if views_match:
                views = views_match.group(1).replace(' ', '')
                return f"""
                    SELECT COUNT(*) FROM videos 
                    WHERE creator_id = {creator_id}
                    AND views_count > {views};
                """

            return f"SELECT COUNT(*) FROM videos WHERE creator_id = {creator_id};"

        # 7. Видео с просмотрами больше N
        views_match = re.search(r'больше ([\d\s]+) просмотров', query)
        if views_match:
            views = views_match.group(1).replace(' ', '')
            return f"SELECT COUNT(*) FROM videos WHERE views_count > {views};"

        # 8. Рост просмотров за дату
        date_match = re.search(r'(\d+) (\w+) (\d+)', query)
        if date_match and ("выросли" in query or "сумме" in query):
            day, month, year = date_match.groups()
            month_num = months.get(month.lower(), 1)
            return f"""
                SELECT COALESCE(SUM(delta_views_count), 0) 
                FROM video_snapshots 
                WHERE DATE(created_at) = '{year}-{month_num:02d}-{int(day):02d}';
            """

        # 9. Разные видео с новыми просмотрами
        if "разных видео получали новые просмотры" in query:
            date_match = re.search(r'(\d+) (\w+) (\d+)', query)
            if date_match:
                day, month, year = date_match.groups()
                month_num = months.get(month.lower(), 1)
                return f"""
                    SELECT COUNT(DISTINCT video_id) 
                    FROM video_snapshots 
                    WHERE DATE(created_at) = '{year}-{month_num:02d}-{int(day):02d}'
                    AND delta_views_count > 0;
                """

        # 10. Универсальный обработчик для месяца (если ничего не подошло, но есть месяц)
        month_num, year = extract_month_year(query)
        if month_num and year:
            if "просмотров" in query and ("суммарное" in query or "набрали" in query):
                return f"""
                    SELECT COALESCE(SUM(views_count), 0) FROM videos 
                    WHERE EXTRACT(MONTH FROM video_created_at) = {month_num}
                    AND EXTRACT(YEAR FROM video_created_at) = {year};
                """
            elif "видео" in query and ("сколько" in query or "количество" in query):
                return f"""
                    SELECT COUNT(*) FROM videos 
                    WHERE EXTRACT(MONTH FROM video_created_at) = {month_num}
                    AND EXTRACT(YEAR FROM video_created_at) = {year};
                """

        # Если ничего не подошло
        return "SELECT 0;"