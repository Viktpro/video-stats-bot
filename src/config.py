import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    def __init__(self):
        # Telegram
        self.bot_token = os.getenv('BOT_TOKEN')

        # GigaChat (может быть пустым)
        self.gigachat_key = os.getenv('GIGACHAT_API_KEY')

        # База данных
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', 5432))
        self.db_name = os.getenv('DB_NAME', 'video_stats')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')


# Создаем один экземпляр для всего приложения
config = Config()