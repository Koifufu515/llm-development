from datetime import datetime,timedelta,timezone
import pytest
from app.storage.job_queue import JobQueue
from app.storage.store import MemoryStore
from app.storage.redis_store import MemorySessionStore

@pytest.mark.asyncio
async def test_expired_lease_is_recovered_and_fenced():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture');j=await q.enqueue('test',{})
 first=(await q.next_jobs())[0]
 row=await q.store.get('async_jobs',j['_id']);row['lease_until']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();await q.store.upsert('async_jobs',row)
 second=(await q.next_jobs())[0]
 assert first['lease_token']!=second['lease_token']
 assert not await q.finish(first,'completed','stale')
 assert await q.finish(second,'completed','fresh')
 assert(await q.store.get('async_jobs',j['_id']))['result']=='fresh'

@pytest.mark.asyncio
async def test_retry_retains_payload_and_exhausts_to_dead_letter():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture',max_attempts=2,retry_base_seconds=0)
 j=await q.enqueue('ingest_document',{'path':'keep-until-terminal'})
 first=(await q.next_jobs())[0];await q.fail(first,RuntimeError('temporary'))
 row=await q.store.get('async_jobs',j['_id']);assert row['status']=='queued'and row['payload']['path']=='keep-until-terminal'
 second=(await q.next_jobs())[0];await q.fail(second,RuntimeError('again'))
 row=await q.store.get('async_jobs',j['_id']);assert row['status']=='failed'and row['dead_letter']
 assert len(await q.store.find('job_dead_letters'))==1

@pytest.mark.asyncio
async def test_duplicate_terminal_job_not_executed():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture');j=await q.enqueue('test',{})
 first=(await q.next_jobs())[0];await q.finish(first,'completed',{})
 assert await q.next_jobs()==[]

@pytest.mark.asyncio
async def test_heartbeat_only_current_owner_can_extend_lease():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture');await q.enqueue('test',{})
 j=(await q.next_jobs())[0];assert await q.heartbeat(j)
 assert not await q.heartbeat({**j,'lease_token':'stale'})

@pytest.mark.asyncio
async def test_repeated_crashed_claims_also_reach_dead_letter():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture',max_attempts=1)
 j=await q.enqueue('test',{});await q.next_jobs()
 row=await q.store.get('async_jobs',j['_id']);row['lease_until']='';await q.store.upsert('async_jobs',row)
 assert await q.next_jobs()==[]
 assert(await q.store.get('async_jobs',j['_id']))['dead_letter']

@pytest.mark.asyncio
async def test_stale_worker_cannot_overwrite_new_progress():
 q=JobQueue(MemoryStore(),MemorySessionStore(),'fixture');await q.enqueue('test',{})
 first=(await q.next_jobs())[0]
 await q.update_progress(first['_id'],{'stage':'wrong'},lease_token='stale')
 assert 'progress'not in(await q.store.get('async_jobs',first['_id']))

@pytest.mark.asyncio
async def test_recovery_does_not_claim_another_queue_namespace():
 s=MemoryStore();a=JobQueue(s,MemorySessionStore(),'a');b=JobQueue(s,MemorySessionStore(),'b')
 j=await b.enqueue('test',{})
 assert await a.next_jobs()==[]
 assert(await s.get('async_jobs',j['_id']))['status']=='queued'
 assert(await b.next_jobs())[0]['_id']==j['_id']
