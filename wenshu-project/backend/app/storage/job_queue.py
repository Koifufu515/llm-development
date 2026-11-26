"""持久作业+至少一次投递；租约/CAS隔离过期Worker，异常可重试和死信。"""
from __future__ import annotations
import os,uuid,logging
from datetime import datetime,timedelta,timezone
from typing import Any
logger=logging.getLogger(__name__)
def _now():return datetime.now(timezone.utc).isoformat()
def _later(seconds):return(datetime.now(timezone.utc)+timedelta(seconds=seconds)).isoformat()

class JobQueue:
 def __init__(self,store,session_store,stream_name,*,max_attempts=3,lease_seconds=120,retry_base_seconds=2):
  self.store=store;self.session_store=session_store;self.stream_name=stream_name
  self.consumer_name=f'worker-{os.getpid()}-{uuid.uuid4().hex[:8]}'
  self.max_attempts=max_attempts;self.lease_seconds=lease_seconds;self.retry_base_seconds=retry_base_seconds
 @property
 def redis(self):return getattr(self.session_store,'_redis',None)
 async def _publish(self,job):
  if self.redis is None:return
  try:
   sid=await self.redis.xadd(self.stream_name,{'job_id':job['_id'],'type':job['type']})
   await self.store.compare_update('async_jobs',job['_id'],{'status':'queued'},{'published_at':_now(),'stream_id':sid})
  except Exception as exc:
   logger.warning('作业已持久化，Redis投递稍后恢复: %s',type(exc).__name__)
 async def enqueue(self,job_type,payload):
  job={'_id':'job_'+uuid.uuid4().hex,'type':job_type,'payload':payload,'queue_name':self.stream_name,'status':'queued','attempts':0,'created_at':_now(),'updated_at':_now()}
  await self.store.upsert('async_jobs',job);await self._publish(job);return job
 async def enqueue_idempotent(self,job_type,payload,key):
  import hashlib
  job_id='scheduled_'+hashlib.sha256((self.stream_name+':'+job_type+':'+key).encode()).hexdigest()
  job={'_id':job_id,'type':job_type,'payload':payload,'queue_name':self.stream_name,'status':'queued','attempts':0,'created_at':_now(),'updated_at':_now()}
  stored=await self.store.create_once('async_jobs',job)
  if stored['status']=='queued'and not stored.get('published_at'):await self._publish(stored)
  return stored
 async def next_jobs(self,count=1,block_ms=1000):
  records=[]
  if self.redis is not None:
   try:
    try:await self.redis.xgroup_create(self.stream_name,'workers',id='0',mkstream=True)
    except Exception as exc:
     if 'BUSYGROUP'not in str(exc):raise
    recovered=await self.redis.xautoclaim(self.stream_name,'workers',self.consumer_name,min_idle_time=int(self.lease_seconds*1000),start_id='0-0',count=count)
    records.extend(recovered[1])
    if not records:
     fresh=await self.redis.xreadgroup('workers',self.consumer_name,{self.stream_name:'>'},count=count,block=max(1,block_ms))
     records.extend(entry for _,entries in fresh for entry in entries)
   except Exception as exc:
    # Redis重启/读超时不使worker退出；Mongo持久作业继续保留。
    logger.warning('队列读取暂不可用: %s',type(exc).__name__)
  candidates=[]
  for sid,fields in records:
   row=await self.store.get('async_jobs',fields['job_id'])
   if not row or row.get('queue_name','wenshu:jobs')!=self.stream_name or row['status']in {'completed','failed'}:
    await self._ack(sid);continue
   row['_stream_id']=sid;candidates.append(row)
  # Durable outbox/租约兜底：xadd前后崩溃、PEL遗失与memory模式均可恢复。
  for row in await self.store.find('async_jobs'):
   if row.get('queue_name', 'wenshu:jobs') != self.stream_name:continue
   if row['status']=='queued'and row.get('retry_at','')<=_now() or row['status']=='running'and row.get('lease_until','')<=_now():
    if not any(c['_id']==row['_id']for c in candidates):candidates.append(row)
  claimed=[]
  for row in candidates:
   if len(claimed)>=count:break
   if row.get('retry_at','')>_now()or(row['status']=='running'and row.get('lease_until','')>_now()):continue
   token=uuid.uuid4().hex
   update={'status':'running','lease_token':token,'lease_owner':self.consumer_name,'lease_until':_later(self.lease_seconds),'attempts':row.get('attempts',0)+1,'updated_at':_now()}
   expected={'status':row['status'],'lease_token':row.get('lease_token')}
   if await self.store.compare_update('async_jobs',row['_id'],expected,update):
    row.update(update);row['_stream_id']=row.get('_stream_id',row.get('stream_id'))
    if update['attempts']>self.max_attempts:
     await self.fail(row,RuntimeError('lease attempts exhausted'))
    else:claimed.append(row)
  return claimed
 async def _ack(self,sid):
  if self.redis is not None and sid:
   try:await self.redis.xack(self.stream_name,'workers',sid)
   except Exception:logger.warning('ACK暂失败，终态作业重投后将跳过')
 async def heartbeat(self,job):
  return await self.store.compare_update('async_jobs',job['_id'],{'status':'running','lease_token':job.get('lease_token')},{'lease_until':_later(self.lease_seconds)})
 async def finish(self,job,status,result=None):
  # 兼容旧调用方传入enqueue回执；只允许当前同一消费者领取的作业。
  if not job.get('lease_token'):
   current=await self.store.get('async_jobs',job['_id'])
   if not current or current.get('lease_owner')!=self.consumer_name:return False
   job={**job,'lease_token':current.get('lease_token')}
  ok=await self.store.compare_update('async_jobs',job['_id'],{'status':'running','lease_token':job.get('lease_token')},{'status':status,'result':result,'updated_at':_now(),'lease_until':''})
  if ok:await self._ack(job.get('_stream_id'))
  return ok
 async def fail(self,job,exc):
  terminal=job.get('attempts',1)>=self.max_attempts
  fields={'status':'failed'if terminal else'queued','result':{'error_type':type(exc).__name__,'error':str(exc)[:500]},'updated_at':_now(),'dead_letter':terminal,'retry_at':_later(self.retry_base_seconds*2**(job.get('attempts',1)-1)),'lease_until':'','published_at':''}
  ok=await self.store.compare_update('async_jobs',job['_id'],{'status':'running','lease_token':job.get('lease_token')},fields)
  if ok:
   await self._ack(job.get('_stream_id'))
   if terminal:
    await self.store.upsert('job_dead_letters',{'_id':job['_id'],**fields,'type':job['type'],'payload':job.get('payload',{})})
    if self.redis is not None:
     try:await self.redis.xadd(self.stream_name+':dlq',{'job_id':job['_id'],'error_type':type(exc).__name__})
     except Exception:pass
  return ok
 async def update_progress(self,job_id,progress,lease_token=None):
  row=await self.store.get('async_jobs',job_id)
  if row and row['status']=='running'and (row.get('lease_token')==lease_token if lease_token else row.get('lease_owner')==self.consumer_name):
   await self.store.compare_update('async_jobs',job_id,{'status':'running','lease_token':row.get('lease_token')},{'progress':progress,'updated_at':_now()})
