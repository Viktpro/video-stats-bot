-- Создание таблицы videos
CREATE TABLE IF NOT EXISTS videos (
    id BIGINT PRIMARY KEY,
    creator_id BIGINT NOT NULL,
    video_created_at TIMESTAMP NOT NULL,
    views_count BIGINT DEFAULT 0,
    likes_count BIGINT DEFAULT 0,
    comments_count BIGINT DEFAULT 0,
    reports_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы video_snapshots
CREATE TABLE IF NOT EXISTS video_snapshots (
    id BIGINT PRIMARY KEY,
    video_id BIGINT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    views_count BIGINT DEFAULT 0,
    likes_count BIGINT DEFAULT 0,
    comments_count BIGINT DEFAULT 0,
    reports_count BIGINT DEFAULT 0,
    delta_views_count BIGINT DEFAULT 0,
    delta_likes_count BIGINT DEFAULT 0,
    delta_comments_count BIGINT DEFAULT 0,
    delta_reports_count BIGINT DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX idx_videos_creator_id ON videos(creator_id);
CREATE INDEX idx_videos_created_at ON videos(video_created_at);
CREATE INDEX idx_snapshots_video_id ON video_snapshots(video_id);
CREATE INDEX idx_snapshots_created_at ON video_snapshots(created_at);
