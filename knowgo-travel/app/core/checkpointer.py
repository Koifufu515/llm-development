from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import Settings


@asynccontextmanager
async def open_checkpointer(settings: Settings):
    # autocommit 用于迁移 DDL；dict_row 是 checkpointer 读取命名字段的要求。
    async with AsyncConnectionPool(
        settings.database_url, min_size=1, max_size=5, open=False,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
    ) as pool:
        await pool.wait(timeout=10)
        saver = AsyncPostgresSaver(pool)
        await saver.setup()
        yield saver
