import asyncio,json,statistics,time,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.knowledge import KnowledgeBase
from app.services.routing import classify,keyword_baseline
from app.core.telemetry import RequestMetrics
from app.config import Settings
from app.utils.llm_factory import get_deepseek_llm

def p95(xs):return sorted(xs)[max(0,int(len(xs)*.95+.999)-1)]

def rag():
 kb=KnowledgeBase();info=kb.load();cases=json.loads((ROOT/'evaluation/rag_cases.json').read_text());results={}
 for rerank in [False,True]:
  rows=[]
  for query,title,index in cases:
   expected=[p for p in kb.parents if p['title']==title][index]['parent_id']
   tick=time.perf_counter();r=kb.search(query,rerank=rerank,use_cache=False);elapsed=time.perf_counter()-tick
   ids=[x['parent_id'] for x in r['results']];rank=ids.index(expected)+1 if expected in ids else None
   rows.append({'query':query,'expected_parent_id':expected,'rank':rank,'seconds':elapsed})
  results['rerank' if rerank else 'no_rerank']={'recall_at_5':sum(r['rank'] is not None for r in rows)/len(rows),'mrr_at_5':sum(1/r['rank'] if r['rank'] else 0 for r in rows)/len(rows),'p95_seconds':p95([r['seconds'] for r in rows]),'rows':rows}
 query=cases[0][0];kb.cache.clear();times=[]
 for i in range(21):
  t=time.perf_counter();r=kb.search(query);times.append({'cache_hit':r['cache_hit'],'seconds':time.perf_counter()-t})
 return {'corpus':info,'sample_count':len(cases),'labeling':'助手按父段人工标注，未经过用户独立复核；小型遗产摘要集，不能外推旅行知识问答准确率','retrieval':results,'cache':{'cold_seconds':times[0]['seconds'],'warm_median_seconds':statistics.median(x['seconds'] for x in times[1:]),'rows':times}}

async def routes():
 cases=json.loads((ROOT/'evaluation/route_cases.json').read_text());semaphore=asyncio.Semaphore(4)
 async def one(row):
  text,channel,intent=row
  async with semaphore:
   metrics=RequestMetrics();tick=time.perf_counter()
   try:
    result=await classify(get_deepseek_llm(Settings()),text,metrics,datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat())
    actual=[result.channel,result.intent];error=None
   except Exception as exc:actual=None;error=type(exc).__name__
   return {'input':text,'expected':[channel,intent],'actual':actual,'correct':actual==[channel,intent],
           'baseline':list(keyword_baseline(text)),'baseline_correct':list(keyword_baseline(text))==[channel,intent],
           'seconds':time.perf_counter()-tick,'error':error,'usage':metrics.snapshot()}
 rows=await asyncio.gather(*(one(r) for r in cases))
 return {'sample_count':len(rows),'concurrency':4,'correct':sum(r['correct'] for r in rows),'accuracy':sum(r['correct'] for r in rows)/len(rows),
         'keyword_baseline_accuracy':sum(r['baseline_correct'] for r in rows)/len(rows),'p95_seconds':p95([r['seconds'] for r in rows]),'rows':rows}
async def main():
 settings=Settings()
 result={'provider':settings.model_provider,'model':settings.qwen_model if settings.model_provider=='qwen' else settings.deepseek_model,'rag':await asyncio.to_thread(rag),'routing':await routes()}
 (ROOT/'reports/quality_benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({'rag':{k:{a:b for a,b in v.items() if a!='rows'} for k,v in result['rag']['retrieval'].items()},'routing':{k:v for k,v in result['routing'].items() if k!='rows'}},ensure_ascii=False))
asyncio.run(main())
