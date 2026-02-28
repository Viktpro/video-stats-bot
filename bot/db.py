import asyncpg
from typing import Optional, Any
from .config import Config

class Database:
    _instance: Optional['Database'] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                Config.DATABASE_URL,
                min_size=5,
                max_size=20
            )

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute_query(self, query: str, *args) -> Any:
        if not self._pool:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            result = await conn.fetch(query, *args)
            return result

db = Database()
