"""真实部署HTTP压测：4次并发预热+60次测量；不缓存查询向量，单独统计重排降级。"""
import asyncio,json,re,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.eval.metrics import percentile
async def main():
 await init_pool()
 async with acquire()as c:
  queries=[r[0]for r in await c.fetch("SELECT q.query FROM eval_queries q JOIN collections k ON k.id=q.collection_id JOIN tenants t ON t.id=k.tenant_id WHERE t.slug='demo'AND k.slug='travel-guide'AND k.status='active'AND q.kind='answerable'ORDER BY q.qid")]
 await close_pool()
 key=re.search(r'qr_[\w-]+',Path('private/knowgo-key.txt').read_text()).group();sem=asyncio.Semaphore(4);rows=[]
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8113',timeout=10,headers={'Authorization':f'Bearer {key}'})as c:
  async def one(i,measured):
   async with sem:
    start=time.perf_counter()
    try:
     r=await c.post('/v1/search',json={'collection':'travel-guide','query':queries[i%len(queries)],'top_k':5})
     data=r.json();es=data.get('evidences',[]);row={'i':i,'query':queries[i%len(queries)],'status':r.status_code,'ms':round((time.perf_counter()-start)*1000,2),'timings':data.get('timings',{}),'rerank_real':any(e.get('rerank_score')is not None for e in es)}
    except Exception as e:row={'i':i,'error':type(e).__name__,'ms':round((time.perf_counter()-start)*1000,2),'status':0,'rerank_real':False}
    if measured:rows.append(row)
    return row
  warm=await asyncio.gather(*(one(i,False)for i in range(4)))
  started=time.perf_counter();await asyncio.gather(*(one(i,True)for i in range(60)));wall=time.perf_counter()-started
 good=[r['ms']for r in rows if r['status']==200];out={'concurrency':4,'warmup':warm,'measured_requests':60,'success':len(good),'failed':60-len(good),'rerank_degraded':sum(r['status']==200 and not r['rerank_real']for r in rows),'p50_ms':percentile(good,50),'p95_ms':percentile(good,95),'p99_ms':percentile(good,99),'qps':round(len(good)/wall,2),'query_vector_cache':False,'rows':sorted(rows,key=lambda r:r['i'])}
 Path('reports/bench-live-http.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in out.items()if k not in ['warmup','rows']},ensure_ascii=False));assert out['failed']==0 and out['rerank_degraded']==0
if __name__=='__main__':asyncio.run(main())
