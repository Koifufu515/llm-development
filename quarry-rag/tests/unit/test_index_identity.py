from uuid import uuid4
import pytest
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.ingest.parsers.base import Section
import quarry.ingest.indexer as indexer

class Embed:
 async def embed(self,texts):return [[1.0]+[0.0]*1023 for _ in texts]

@pytest.mark.asyncio
async def test_normalized_id_reuse_does_not_leave_old_original_text(monkeypatch):
 await init_pool();tenant=None
 try:
  async with acquire()as c:
   tenant=await c.fetchval("INSERT INTO tenants(slug,name)VALUES($1,'引用保真回归')RETURNING id",'test-'+uuid4().hex)
   coll=await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim)VALUES($1,'test','test','fixture',1024)RETURNING id",tenant)
   doc=await c.fetchval("INSERT INTO documents(collection_id,source_uri,sha256)VALUES($1,'a.md','test')RETURNING id",coll)
  monkeypatch.setattr(indexer,'get_embedder',lambda:Embed())
  async def put(text):
   return await indexer.index_document(doc,coll,'test','a.md',1,['public'],[Section(['正文'],text,0,len(text))])
  await put('门票 120元。');stats=await put('门票  120元。')
  assert stats['vectorized']==0
  async with acquire()as c:
   rows=await c.fetch('SELECT content,char_start,char_end FROM chunks WHERE collection_id=$1',coll)
  assert rows and all(r['content']=='门票  120元。' and r['char_end']==len(r['content'])for r in rows)
 finally:
  if tenant:
   async with acquire()as c:await c.execute('DELETE FROM tenants WHERE id=$1',tenant)
  await close_pool()
