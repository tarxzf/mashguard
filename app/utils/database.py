from psycopg_pool import AsyncConnectionPool
from psycopg.abc import Params
from psycopg.errors import ProgrammingError
from typing import Optional, Iterable, Tuple, List


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn

        self.pool: Optional[AsyncConnectionPool] = None
    
    async def initialize(self):
        if self.pool is None:
            self.pool = AsyncConnectionPool(self.dsn, open=False)
            await self.pool.open()

    async def execute(self, query: str, params: Optional[Params] = None, *, commit: Optional[bool] = True, **kwargs):
        async with self.pool.connection() as connection:
            async with connection.pipeline():
                await connection.execute(query, params, **kwargs)
                if commit:
                    await connection.commit()

    async def executemany(self, query: str, params: Iterable[Params], *, commit: Optional[bool] = True, **kwargs):
        async with self.pool.connection() as connection:
            async with connection.pipeline():
                async with connection.cursor() as cursor:
                    await cursor.executemany(query, params, **kwargs)
                if commit:
                    await connection.commit()

    async def fetchone(self, query: str, params: Optional[Params] = None, **kwargs) -> Optional[Tuple]:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params, **kwargs)
                row: Optional[Tuple] = await cursor.fetchone()
        return row

    async def fetchall(self, query: str, params: Optional[Params] = None, **kwargs) -> List[Optional[Tuple]]:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params, **kwargs)
                rows: List[Optional[Tuple]] = await cursor.fetchall()
        return rows
    
    async def fetchmany(self, query: str, params: Iterable[Params], **kwargs) -> Optional[List[Tuple]]:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.executemany(query, params, **kwargs)
                try:
                    rows: List[Tuple] = await cursor.fetchmany()
                except ProgrammingError:
                    return None
        return rows
    
    async def close(self):
        if isinstance(self.pool, AsyncConnectionPool):
            await self.pool.close()
