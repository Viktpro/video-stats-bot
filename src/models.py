from datetime import datetime

class Video:
    """Простая модель видео"""
    def __init__(self, id, creator_id, created_at, views=0, likes=0, comments=0, reports=0):
        self.id = id
        self.creator_id = creator_id
        self.created_at = created_at
        self.views = views
        self.likes = likes
        self.comments = comments
        self.reports = reports

class Snapshot:
    """Модель почасового снимка"""
    def __init__(self, video_id, created_at, views=0, likes=0, comments=0, reports=0,
                 delta_views=0, delta_likes=0, delta_comments=0, delta_reports=0):
        self.video_id = video_id
        self.created_at = created_at
        self.views = views
        self.likes = likes
        self.comments = comments
        self.reports = reports
        self.delta_views = delta_views
        self.delta_likes = delta_likes
        self.delta_comments = delta_comments
        self.delta_reports = delta_reports