"""术语候选从原文提取；只有管理员审核后才写入查询改写词表。"""
import re,hashlib
from datetime import datetime,timezone

class GlossaryExtractor:
 def __init__(self,store):self.store=store
 async def extract(self,doc):
  chunks=await self.store.list_chunks_by_doc(doc['_id']);out=[]
  pattern=re.compile(r'([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9]{1,24})[（(](?:以下)?简称[：:"“\s]*([^）)"”\s]{1,16})["”]?[）)]')
  for chunk in chunks:
   for full,alias in pattern.findall(chunk.get('content','')):
    key=hashlib.sha256(f"{doc['dept_id']}:{full}:{alias}".encode()).hexdigest()
    item={'_id':'term_'+key,'canonical':full,'synonyms':[alias],'dept_id':doc['dept_id'],'source_doc_id':doc['_id'],'source_chunk_id':chunk['_id'],'status':'pending','created_at':datetime.now(timezone.utc)}
    await self.store.create_once('glossary_candidates',item);out.append(item)
  return out
 async def review(self,id_,actor,approved):
  item=await self.store.get('glossary_candidates',id_)
  if not item:raise KeyError('术语候选不存在')
  source=await self.store.get_document(item['source_doc_id'])
  if approved and (not source or source.get('status')!='active'):raise ValueError('术语来源已失效')
  item.update(status='approved' if approved else 'rejected',reviewed_by=actor,reviewed_at=datetime.now(timezone.utc))
  await self.store.upsert('glossary_candidates',item)
  if approved:await self.store.upsert('glossary',{**item,'status':'active'})
  return item
