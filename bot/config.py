import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
    
    if not BOT_TOKEN or not DATABASE_URL:
        raise ValueError("Не заданы обязательные переменные окружения")
