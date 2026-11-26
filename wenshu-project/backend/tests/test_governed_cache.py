import pytest
from app.storage.store import MemoryStore
from app.storage.redis_store import MemorySessionStore
from app.retrieval.cache import GovernedAnswerCache
from app.harness.base import Answer
from app.config import Settings
from app.llm.embeddings import EmbeddingClient

@pytest.mark.asyncio
async def test_cache_signature_identity_version_and_live_evidence():
 store=MemoryStore();cache=GovernedAnswerCache(store,MemorySessionStore(),'qwen')
 doc={'_id':'d','dept_id':'a','status':'active','version':'1'};await store.insert_document(doc)
 chunk={'_id':'d:0','doc_id':'d','content':'甲','content_hash':'hash'};await store.insert_chunks([chunk])
 key=await cache.key('问',['a'],'u','student','')
 assert key!=await cache.key('问',['a'],'other','student','')
 await cache.put(key,Answer(content='甲',verification={'passed':True}),[chunk])
 assert await cache.get(key)
 await store.update_document('d',{'status':'archived'})
 assert not await cache.get(key)
 assert key!=await cache.key('问',['a'],'u','student','')

@pytest.mark.asyncio
async def test_query_embedding_lru_model_signature_and_defensive_copy():
 c=EmbeddingClient(Settings(embedding_provider='hash',embedding_dim=128))
 a=await c.embed_query('制度');a[0]=999
 b=await c.embed_query('制度');assert b[0]!=999
 assert len(c._query_cache)==1
 c.model='new-model';await c.embed_query('制度');assert len(c._query_cache)==2
