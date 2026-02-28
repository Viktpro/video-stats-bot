import json
import asyncio
import asyncpg
import os
from datetime import datetime

async def load_data():
    await asyncio.sleep(5)
    
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM videos")
        if count > 0:
            print("Данные уже загружены")
            return
        
        with open("data/videos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for video in data:
            await conn.execute("""
                INSERT INTO videos (id, creator_id, video_created_at, views_count, 
                                   likes_count, comments_count, reports_count)
                VALUES (, , , , , , )
            """, 
                video["id"], 
                video["creator_id"], 
                datetime.fromisoformat(video["video_created_at"].replace("Z", "+00:00")),
                video["views_count"],
                video["likes_count"],
                video["comments_count"],
                video["reports_count"]
            )
            
            for snapshot in video.get("snapshots", []):
                await conn.execute("""
                    INSERT INTO video_snapshots 
                    (id, video_id, views_count, likes_count, comments_count, reports_count,
                     delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count,
                     created_at)
                    VALUES (, , , , , , , , , , )
                """,
                    snapshot["id"],
                    video["id"],
                    snapshot["views_count"],
                    snapshot["likes_count"],
                    snapshot["comments_count"],
                    snapshot["reports_count"],
                    snapshot["delta_views_count"],
                    snapshot["delta_likes_count"],
                    snapshot["delta_comments_count"],
                    snapshot["delta_reports_count"],
                    datetime.fromisoformat(snapshot["created_at"].replace("Z", "+00:00"))
                )
        
        print(f"Загружено {len(data)} видео")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(load_data())
