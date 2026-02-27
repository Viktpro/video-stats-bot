-- Таблица с видео
CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    creator_id TEXT NOT NULL,
    video_created_at TIMESTAMP NOT NULL,
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    reports_count INTEGER DEFAULT 0
);

-- Таблица с почасовыми снимками
CREATE TABLE IF NOT EXISTS video_snapshots (
    id SERIAL PRIMARY KEY,
    video_id TEXT REFERENCES videos(id) ON DELETE CASCADE,
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    reports_count INTEGER DEFAULT 0,
    delta_views_count INTEGER DEFAULT 0,
    delta_likes_count INTEGER DEFAULT 0,
    delta_comments_count INTEGER DEFAULT 0,
    delta_reports_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(video_id, created_at)
);

-- Индексы для быстрого поиска
CREATE INDEX idx_videos_creator ON videos(creator_id);
CREATE INDEX idx_snapshots_video ON video_snapshots(video_id);
CREATE INDEX idx_snapshots_date ON video_snapshots(created_at);