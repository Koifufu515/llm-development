import asyncio
import pytest
from app.storage.redis_store import MemorySessionStore
from app.utils.distributed_budget import DistributedBudget

@pytest.mark.asyncio
async def test_atomic_user_and_dept_budget_under_concurrency():
 budget=DistributedBudget(MemorySessionStore())
 allowed=await asyncio.gather(*[budget.take([('user','u',3),('dept','d',5)])for _ in range(12)])
 assert sum(allowed)==3
 # 拒绝请求不会吞掉部门剩余额度。
 assert await budget.take([('user','other',3),('dept','d',5)])
 assert await budget.take([('user','another',3),('dept','d',5)])
 assert not await budget.take([('user','last',3),('dept','d',5)])

@pytest.mark.asyncio
async def test_unconnected_redis_cannot_silently_disable_limits():
 class RedisStore:_redis=None
 with pytest.raises(RuntimeError):await DistributedBudget(RedisStore()).take([('user','u',1)])
