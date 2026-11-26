from uuid import uuid4
import pytest
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.api.logs import log_query

@pytest.mark.asyncio
async def test_upstream_string_request_id_is_persisted():
 await init_pool();rid='req_'+uuid4().hex
 try:
  await log_query(request_id=rid,caller_id='acceptance',collection='travel-guide',query='日志ID验收',top_k=1,status=200)
  async with acquire()as c:
   assert await c.fetchval('SELECT count(*)FROM query_logs WHERE request_id::text=$1',rid)==1
 finally:
  async with acquire()as c:await c.execute('DELETE FROM query_logs WHERE request_id::text=$1',rid)
  await close_pool()
