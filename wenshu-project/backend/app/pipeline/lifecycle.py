"""文档状态、版本历史与有效期提醒，保留所有原文和审计。"""
from datetime import datetime, timedelta, timezone
import hashlib
from app.memory.policy import parse_time

TRANSITIONS = {
 'draft': {'review','deleted'}, 'review': {'draft','active','deleted'},
 'active': {'review','archived','deleted'}, 'archived': {'review','active','deleted'},
 'deleted': set(), 'failed': {'draft','deleted'},
}

class DocumentLifecycle:
 def __init__(self,store,indexer):self.store=store;self.indexer=indexer
 async def transition(self,doc_id,status,actor):
  doc=await self.store.get_document(doc_id)
  if not doc:raise KeyError('文档不存在')
  current=doc.get('status','draft')
  if status == current:return doc
  if status not in TRANSITIONS.get(current,set()):raise ValueError(f'不允许从{current}进入{status}')
  if status=='active' and doc.get('vector_status')!='ready':raise ValueError('向量索引未就绪')
  await self.indexer.set_status(doc_id,status)
  await self.store.upsert('document_audit',{'_id':f'{doc_id}:{datetime.now(timezone.utc).isoformat()}', 'doc_id':doc_id,'from':current,'to':status,'actor_id':actor,'created_at':datetime.now(timezone.utc)})
  return await self.store.get_document(doc_id)
 async def history(self,doc_id):
  doc=await self.store.get_document(doc_id)
  if not doc:return []
  rows=await self.store.list_documents(dept_id=doc['dept_id'])
  return sorted([d for d in rows if d.get('title')==doc.get('title')],key=lambda d:d.get('created_at',''))
 async def remind_expiring(self,now=None,days=30):
  now=now or datetime.now(timezone.utc);out=[]
  for doc in await self.store.list_documents(status='active'):
   expiry=parse_time(doc.get('expiry_date'))
   if not expiry or expiry>now+timedelta(days=days):continue
   key=hashlib.sha256(f"expiry:{doc['_id']}:{expiry.isoformat()}".encode()).hexdigest()
   row={'_id':'notice_'+key,'type':'document_expiry','dept_id':doc['dept_id'],'doc_id':doc['_id'],'title':doc['title'],'expiry_date':expiry,'expired':expiry<=now,'status':'unread','created_at':now}
   await self.store.create_once('notifications',row);out.append(row)
  return out
