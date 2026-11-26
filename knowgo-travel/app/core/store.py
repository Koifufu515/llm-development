"""长期偏好与业务记录使用独立namespace，和thread checkpoint分离。"""
from contextlib import asynccontextmanager
from langgraph.store.postgres.aio import AsyncPostgresStore
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

@asynccontextmanager
async def open_store(settings):
    async with AsyncConnectionPool(settings.database_url, min_size=1, max_size=5, open=False,
        kwargs={"autocommit":True,"prepare_threshold":0,"row_factory":dict_row}) as pool:
        await pool.wait(timeout=10)
        store=AsyncPostgresStore(pool)
        await store.setup()
        yield store

async def update_preferences(store, user_id, updates):
    namespace=("users",str(user_id),"preferences")
    before=await store.aget(namespace,"profile")
    merged={**(before.value if before else {}),**updates}
    await store.aput(namespace,"profile",merged)
    return merged
