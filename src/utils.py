import re
from datetime import datetime


def format_number(num):
    """Форматирует число с разделителями тысяч"""
    return f"{num:,}".replace(",", " ")


def parse_date(text):
    """Пытается найти дату в тексте"""
    # Ищем "28 ноября 2025"
    match = re.search(r'(\d{1,2})\s+([а-я]+)\s+(\d{4})', text.lower())
    if match:
        day, month, year = match.groups()

        months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }

        if month in months:
            return f"{year}-{months[month]:02d}-{int(day):02d}"

    return None