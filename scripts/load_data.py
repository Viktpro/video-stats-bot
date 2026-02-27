#!/usr/bin/env python
"""
Скрипт для ручной загрузки данных в базу.
Использовать, если нужно перезагрузить данные.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.database import db

async def main():
    print("Загрузка данных...")
    await db.connect()
    await db.load_data("data/videos.json")
    await db.close()
    print("Готово!")

if __name__ == "__main__":
    asyncio.run(main())