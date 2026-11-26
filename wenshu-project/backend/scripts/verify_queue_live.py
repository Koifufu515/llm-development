"""仅创建独立UUID队列和测试作业，不调用模型、不处理原文档；真实kill领取进程。"""
import asyncio,json,os,sys,uuid,signal
from pathlib import Path
from dotenv import dotenv_values
from app.config import Settings
from app.storage.mongodb import MongoDB
from app.storage.store import MongoStore
from app.storage.redis_store import RedisSessionStore
from app.storage.job_queue import JobQueue

async def main():
 settings=Settings();mongo=MongoDB(settings);await mongo.connect();store=MongoStore(mongo)
 sessions=RedisSessionStore(settings);await sessions.connect()
 stream='wenshu:verify:'+uuid.uuid4().hex;queue=JobQueue(store,sessions,stream,lease_seconds=.6,max_attempts=3,retry_base_seconds=0);ids=[]
 try:
  job=await queue.enqueue('fixture_only',{'fixture':True});ids.append(job['_id'])
  child='''import asyncio,sys
from app.config import Settings
from app.storage.mongodb import MongoDB
from app.storage.store import MongoStore
from app.storage.redis_store import RedisSessionStore
from app.storage.job_queue import JobQueue
async def run():
 s=Settings();m=MongoDB(s);await m.connect();r=RedisSessionStore(s);await r.connect();q=JobQueue(MongoStore(m),r,sys.argv[1],lease_seconds=.6)
 j=(await q.next_jobs(block_ms=10))[0];print('CLAIMED',flush=True);await asyncio.sleep(600)
asyncio.run(run())'''
  proc=await asyncio.create_subprocess_exec(sys.executable,'-u','-c',child,stream,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
  while True:
   line=await asyncio.wait_for(proc.stdout.readline(),15)
   if b'CLAIMED'in line:break
   if not line:raise RuntimeError('领取子进程未就绪')
  proc.kill();await proc.wait();await asyncio.sleep(.7)
  reclaimed=(await queue.next_jobs(block_ms=10))[0];assert reclaimed['_id']==job['_id'];assert reclaimed['attempts']==2
  assert await queue.finish(reclaimed,'completed',{'reclaimed':True})
  assert await sessions.redis.xpending(stream,'workers')=={'pending':0,'min':None,'max':None,'consumers':[]}
  j=await queue.enqueue('fixture_only',{});ids.append(j['_id'])
  for _ in range(3):
   next_job=(await queue.next_jobs(block_ms=10))[0];await queue.fail(next_job,RuntimeError('injected fixture failure'))
  failed=await store.get('async_jobs',j['_id']);assert failed['dead_letter']and failed['status']=='failed'
  assert await sessions.redis.xlen(stream+':dlq')==1
  result={'real_mongo_redis':True,'killed_child_exitcode':proc.returncode,'expired_claim_recovered':True,'attempts_after_recovery':reclaimed['attempts'],'completed_ack_pending':0,'failures_to_dlq':3,'production_jobs_untouched':True,'models_called':False}
  out=Path(os.environ.get('WENSHU_REPORT_DIR','../reports'));out.mkdir(exist_ok=True,parents=True);(out/'queue-live.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
 finally:
  for id_ in ids:
   await store.delete('async_jobs',id_);await store.delete('job_dead_letters',id_)
  await sessions.redis.delete(stream,stream+':dlq');await sessions.close();await mongo.close()

if __name__=='__main__':asyncio.run(main())
