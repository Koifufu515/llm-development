"""Redis答案缓存：身份/记忆/策略/文档版本签名，命中后仍回查官方事实。"""
import hashlib,json
from app.memory.facts import document_readable

class GovernedAnswerCache:
 def __init__(self,store,sessions,model):self.store=store;self.sessions=sessions;self.model=model
 async def eligible(self):
  if await self.store.find('experiments',{'status':'running'}):return False
  for skill in await self.store.list_skills(status='active'):
   if float(skill.get('gray_percent',1))<1 or (skill.get('parameter_experiment')or{}).get('enabled'):return False
  return True
 async def key(self,query,depts,user,role,memory):
  docs=await self.store.list_documents(status='active')
  versions=sorted((d['_id'],d.get('version'),str(d.get('updated_at','')),d.get('vector_status'))for d in docs)
  strategies=[]
  for kind in ('skills','hooks','rules'):
   for item in await self.store.find(kind,{'status':'active'}):
    strategies.append((kind,item['_id'],hashlib.sha256(json.dumps({k:v for k,v in item.items() if k not in {"metrics","updated_at","last_triggered"}},sort_keys=True,default=str,ensure_ascii=False).encode()).hexdigest()))
  payload=[self.model,query,sorted(depts),user,role,memory,versions,sorted(strategies)]
  return 'answer:v2:'+hashlib.sha256(json.dumps(payload,sort_keys=True,default=str,ensure_ascii=False).encode()).hexdigest()
 async def get(self,key,role="student"):
  row=await self.sessions.cache_get(key)
  if not row:return None
  for chunk in row.get('chunks',[]):
   current=await self.store.get('chunks',chunk['_id'])
   doc=await self.store.get_document(chunk['doc_id'])
   if not current or not document_readable(doc,role) or current.get('content_hash')!=chunk.get('content_hash'):return None
  return row
 async def put(self,key,answer,chunks):
  if answer.verification.get('passed') and chunks:
   await self.sessions.cache_set(key,{'answer':answer.to_dict(),'chunks':chunks},ttl=3600)
