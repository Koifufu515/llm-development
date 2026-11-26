from uuid import uuid4
import pytest
from quarry.infra.db import init_pool,close_pool,acquire
import quarry.pipeline as pipeline

@pytest.mark.asyncio
async def test_same_slug_routes_to_explicit_tenant(monkeypatch):
 await init_pool();tenants=[];ids=[];seen=[]
 try:
  async with acquire()as c:
   for _ in range(2):
    tid=await c.fetchval("INSERT INTO tenants(slug,name)VALUES($1,'隔离验收')RETURNING id",'scope-'+uuid4().hex);tenants.append(tid)
    ids.append(await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim)VALUES($1,'shared','shared','text-embedding-v4',1024)RETURNING id",tid))
  async def retrieval(**kw):seen.append(kw['collection_id']);return []
  monkeypatch.setattr(pipeline,'hybrid_search',retrieval)
  for t in tenants:await pipeline.search_evidence('shared','q',['public'],tenant_id=t,use_rerank=False,use_facts=False)
  assert seen==ids
 finally:
  async with acquire()as c:await c.execute('DELETE FROM tenants WHERE id=ANY($1::uuid[])',tenants)
  await close_pool()
