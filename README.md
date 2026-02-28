# 🎥 Video Stats Telegram Bot

## 🚀 Локальный запуск
```bash
git clone https://github.com/Viktpro/video-stats-bot.git
cd video-stats-bot
cp .env.example .env
# Добавьте данные в data/videos.json
docker-compose up --build

🔑 .env.example
env
BOT_TOKEN=                   # @BotFather
GIGACHAT_CREDENTIALS=        # SberCloud (Client ID:Secret в Base64)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/video_stats

🏗 Архитектура
text
Telegram → Bot (aiogram) → SimpleLLM (текст→SQL) → PostgreSQL → Ответ

🔄 Примеры преобразования
sql
-- "Сколько всего видео?"
SELECT COUNT(*) FROM videos;
-- "Просмотры за июнь 2025"
SELECT SUM(views_count) FROM videos 
WHERE EXTRACT(MONTH FROM video_created_at)=6 
AND EXTRACT(YEAR FROM video_created_at)=2025;

📊 Промпт для LLM
sql
Таблицы:
- videos(id, creator_id, video_created_at, views_count, likes_count, comments_count)
- video_snapshots(id, video_id, views_count, likes_count, delta_views_count, 
  delta_likes_count, delta_comments_count, created_at)

Правила:
1. Возвращай только SQL
2. Одно число в результате
3. UUID в кавычках, числа без
4. Используй COALESCE для SUM

Бот: @elly_stats_bot
