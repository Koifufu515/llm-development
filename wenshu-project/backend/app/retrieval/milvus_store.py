"""真实独立Milvus候选平面；正文和最终权限判定始终回MongoDB。"""
from __future__ import annotations
import asyncio,json,math
from typing import Any
from app.retrieval.vector_store import VectorStore

class MilvusVectorStore(VectorStore):
 def __init__(self,settings):
  self.settings=settings;self.name=settings.milvus_collection;self.dim=settings.embedding_dim
  self._client=None;self._lock=asyncio.Lock()
 async def _ready(self):
  async with self._lock:
   if self._client is None:
    await asyncio.to_thread(self._connect)
  return self._client
 def _connect(self):
  from pymilvus import MilvusClient,DataType
  c=MilvusClient(uri=self.settings.milvus_uri,token=self.settings.milvus_token,timeout=15)
  if not c.has_collection(self.name):
   schema=c.create_schema(auto_id=False,enable_dynamic_field=True)
   schema.add_field('id',DataType.VARCHAR,is_primary=True,max_length=256)
   schema.add_field('vector',DataType.FLOAT_VECTOR,dim=self.dim)
   schema.add_field('dept_id',DataType.VARCHAR,max_length=128)
   schema.add_field('doc_id',DataType.VARCHAR,max_length=128)
   idx=c.prepare_index_params();idx.add_index(field_name='vector',index_type='HNSW',metric_type='COSINE',params={'M':16,'efConstruction':200})
   c.create_collection(self.name,schema=schema,index_params=idx,consistency_level='Strong')
  desc=c.describe_collection(self.name)
  vector=next(f for f in desc['fields']if f['name']=='vector')
  if int(vector['params']['dim'])!=self.dim:
   raise ValueError('Milvus集合维度不匹配，须使用新集合重建，禁止混合模型')
  c.load_collection(self.name);self._client=c
 def _check(self,vector):
  if len(vector)!=self.dim or not all(math.isfinite(float(x))for x in vector):raise ValueError('非法向量维度/数值')
 async def add(self,id_:str,vector:list[float],metadata:dict[str,Any]):
  self._check(vector);c=await self._ready()
  row={**metadata,'id':id_,'vector':vector,'embedding_model':self.settings.embedding_model}
  await asyncio.to_thread(c.upsert,self.name,[row])
 async def search(self,vector,top_k=10,dept_id=None):
  self._check(vector);c=await self._ready()
  filters=[f'embedding_model == {json.dumps(self.settings.embedding_model)}']
  if dept_id:filters.append('dept_id == '+json.dumps(dept_id))
  result=await asyncio.to_thread(c.search,self.name,[vector],filter=' and '.join(filters),limit=top_k,
   output_fields=['doc_id','dept_id','chunk_index'],search_params={'metric_type':'COSINE','params':{'ef':max(64,top_k)}})
  return [{'id':r['id'],'score':float(r['distance']),**r.get('entity',{})}for r in result[0]]
 async def delete_by_doc(self,doc_id):
  c=await self._ready();await asyncio.to_thread(c.delete,self.name,filter='doc_id == '+json.dumps(doc_id))
 async def count(self):
  c=await self._ready();await asyncio.to_thread(c.flush,self.name)
  return int((await asyncio.to_thread(c.get_collection_stats,self.name))['row_count'])
 async def close(self):
  if self._client:await asyncio.to_thread(self._client.close)
