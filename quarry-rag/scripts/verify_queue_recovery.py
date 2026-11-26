"""真实Redis：领取进程被杀后接管、ACK、三次失败死信；仅用隔离Stream。"""
import asyncio,json,sys,os
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.ingest.queue import get_redis
import quarry.ingest.worker as w

async def main():
 await init_pool();r=get_redis();stream='quarry:acceptance:'+uuid4().hex;group='recovery';dead=stream+':dead';tenant=None
 marker=Path('private')/('claimed-'+uuid4().hex+'.json');out={}
 w.STREAM_KEY=stream;w.GROUP_NAME=group;w.DEAD_KEY=dead;w.CLAIM_MIN_IDLE_MS=0
 try:
  await r.xgroup_create(stream,group,id='0',mkstream=True)
  async with acquire()as c:
   coll=await c.fetchrow("SELECT c.id,c.slug FROM collections c WHERE c.slug='travel-guide' AND status='active'")
   doc=await c.fetchval("SELECT id FROM documents WHERE collection_id=$1 AND status='ready' ORDER BY source_uri LIMIT 1",coll['id'])
  msg=await r.xadd(stream,{'document_id':str(doc),'stage':'parsing'})
  child='''import asyncio,sys,json\nfrom pathlib import Path\nfrom quarry.ingest.queue import get_redis\nasync def m():\n r=get_redis();x=await r.xreadgroup(sys.argv[2],"victim",{sys.argv[1]:">"},count=1,block=5000);Path(sys.argv[3]).write_text(json.dumps(x));await asyncio.sleep(30)\nasyncio.run(m())'''
  proc=await asyncio.create_subprocess_exec(sys.executable,'-c',child,stream,group,str(marker),stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.DEVNULL)
  for _ in range(50):
   if marker.exists():break
   if proc.returncode is not None:raise RuntimeError('领取进程提前退出')
   await asyncio.sleep(.1)
  assert marker.exists();proc.kill();await proc.wait()
  assert (await r.xpending(stream,group))['pending']==1
  await w._claim_stale(r)
  assert (await r.xpending(stream,group))['pending']==0
  out['killed_reader_then_real_ingest_claim_ack']=True
  invalid=str(uuid4());bad=await r.xadd(stream,{'document_id':invalid,'stage':'parsing'})
  messages=await r.xreadgroup(group,'dead-check',{stream:'>'},count=1)
  await w._handle(r,bad,messages[0][1][0][1])
  for _ in range(3):await w._claim_stale(r)
  assert (await r.xpending(stream,group))['pending']==0
  rows=await r.xrange(dead);assert len(rows)==1 and rows[0][1]['times_delivered']=='3'
  out['three_deliveries_dead_letter']=True;out['dead_letter']=rows[0][1];out['victim_exitcode']=proc.returncode
 finally:
  await r.delete(stream,dead);await r.aclose();await close_pool();marker.unlink(missing_ok=True)
 Path('reports/queue-recovery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
