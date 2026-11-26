import pytest
from app.config import Settings
from app.llm.embeddings import EmbeddingClient
from app.llm.relay import RelayClient
from app.llm.client import LLMError
from app.retrieval.vector_store import build_vector_store
from app.harness.agents.retrieval_agent import RetrievalAgent
from app.storage.store import MemoryStore

class FailedRelay:
 async def embed(self,*args,**kwargs):raise LLMError('upstream unavailable')

@pytest.mark.asyncio
async def test_real_embedding_failure_never_returns_hash():
 c=EmbeddingClient(Settings(embedding_provider='relay',relay_api_key='fixture',embedding_dim=4),FailedRelay())
 with pytest.raises(LLMError):await c.embed(['制度'])

@pytest.mark.asyncio
async def test_embedding_batch_shape_is_validated():
 class Wrong:
  async def embed(self,*a,**k):return [[1.,0.]]
 c=EmbeddingClient(Settings(embedding_provider='relay',relay_api_key='fixture',embedding_dim=4),Wrong())
 with pytest.raises(LLMError):await c.embed(['第一条','第二条'])

@pytest.mark.asyncio
async def test_rerank_matches_result_index_not_response_order():
 c=RelayClient(Settings(relay_api_key='fixture'))
 async def response(*a,**k):return {'results':[{'index':1,'relevance_score':.9},{'index':0,'relevance_score':.2}]}
 c._post_json=response
 assert await c.rerank('问',['甲','乙'])==[.2,.9]

def test_unknown_vector_backend_fails_closed():
 with pytest.raises(ValueError):build_vector_store('typo')

@pytest.mark.asyncio
async def test_persistent_chunk_department_rechecked():
 store=MemoryStore();await store.insert_document({'_id':'doc','dept_id':'secret','status':'active'})
 await store.insert_chunks([{'_id':'chunk','doc_id':'doc','dept_id':'secret','content':'机密'}])
 class Emb:
  async def embed_query(self,q):return [1.,0.]
 class Hybrid:
  async def retrieve(self,*a,**k):return [{'id':'chunk','score':1}]
 agent=RetrievalAgent(Hybrid(),Emb(),store)
 assert await agent.retrieve(['问'],['public'])==[]

@pytest.mark.asyncio
async def test_vector_only_body_hydrated_before_remote_rerank():
 from app.retrieval.hybrid import HybridRetriever
 store=MemoryStore()
 await store.insert_document({'_id':'doc','dept_id':'public','status':'active'})
 await store.insert_chunks([{'_id':'chunk','doc_id':'doc','dept_id':'public','content':'官方原文'}])
 class BM:
  def search(self,*a,**k):return []
 class VS:
  async def search(self,*a,**k):return [{'id':'chunk','score':1}]
 class Rank:
  async def rerank(self,q,candidates,**kw):
   assert candidates[0]['content']=='官方原文'
   return candidates
 hybrid=HybridRetriever(BM(),VS(),Rank(),store=store)
 assert (await hybrid.retrieve('问',[1.],dept_id='public'))[0]['content']=='官方原文'

@pytest.mark.asyncio
async def test_embedding_outage_retains_bm25_without_hash():
 from app.retrieval.hybrid import HybridRetriever
 from app.retrieval.bm25 import BM25Index
 from app.retrieval.reranker import HeuristicReranker
 store=MemoryStore()
 chunk={'_id':'chunk','doc_id':'doc','dept_id':'public','content':'退课截止第八周'}
 await store.insert_document({'_id':'doc','dept_id':'public','status':'active'})
 await store.insert_chunks([chunk]);bm=BM25Index();bm.index([chunk])
 class VS:
  async def search(self,*a,**k):raise AssertionError('embedding故障不能伪造向量')
 class Emb:
  async def embed_query(self,*a):raise LLMError('offline')
 agent=RetrievalAgent(HybridRetriever(bm,VS(),HeuristicReranker()),Emb(),store)
 assert (await agent.retrieve(['退课'],['public']))[0]['content']=='退课截止第八周'

@pytest.mark.asyncio
async def test_private_roster_filtered_before_model_rerank():
 from app.retrieval.hybrid import HybridRetriever
 store=MemoryStore();await store.insert_document({'_id':'d','dept_id':'a','status':'active','access_roles':['admin']})
 await store.insert_chunks([{'_id':'c','doc_id':'d','dept_id':'a','content':'名单原文'}])
 class BM:
  def search(self,*a,**kw):return [{'id':'c'}]
 class VS:
  async def search(self,*a,**kw):return []
 class Rank:
  async def rerank(self,q,candidates,**kw):return candidates
 hybrid=HybridRetriever(BM(),VS(),Rank(),store=store)
 assert await hybrid.retrieve('名单',[1],dept_id='a',user_role='student')==[]
 assert len(await hybrid.retrieve('名单',[1],dept_id='a',user_role='admin'))==1
