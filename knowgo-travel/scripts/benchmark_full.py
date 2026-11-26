from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
TODAY=datetime.now(ZoneInfo("Asia/Shanghai")).date()
import asyncio,json,time,statistics
from pathlib import Path
from app.main import app
from app.full.capabilities import transport_segment
from app.full.routing import route
from app.core.telemetry import RequestMetrics
CASES=[('上海去北京三天，帮我安排一下',[],{},'planning'),('想去附近玩两天',[],{},'planning'),('两个人，每人3000',['assistant:几个人出行，预算多少？'],{},'planning'),('苏州',['assistant:你想去哪个目的地？'],{},'planning'),('改成高铁出行',[],{'current_step':'accommodation_planning'},'planning'),('确认',[],{'current_step':'destination_recommendation'},'planning'),('我想重新规划',[],{'current_step':'budget_summarization'},'planning'),('南京多待一天',['assistant:上海苏州南京四天方案已生成'],{'current_step':'budget_summarization'},'planning'),('你好',[],{},'plain'),('介绍一下你自己',[],{},'plain'),('你能做什么',[],{},'plain'),('谢谢',[],{'current_step':'budget_summarization'},'plain'),('什么是LangGraph',[],{},'plain'),('讲一个笑话',[],{},'plain'),('2加2等于几',[],{},'plain'),('再见',[],{},'plain')]
async def main():
 out={'scope':'本机开发验收，真实接口；有限样本，非线上SLA或业务准确率'}
 async with app.router.lifespan_context(app):
  s=app.state.full;rows=[]
  for msg,h,state,expected in CASES:
   start=time.perf_counter();actual=await route(s,msg,h,state);rows.append({'message':msg,'history':h,'state':state,'expected':expected,'actual':actual,'seconds':round(time.perf_counter()-start,4)})
  out['routing']=rows;Path('reports/full_benchmarks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('route',sum(r['actual']==r['expected'] for r in rows),len(rows),flush=True)
  legs=[{'segment_id':'s1','from':'上海','to':'苏州','date':(TODAY+timedelta(days=1)).isoformat()},{'segment_id':'s2','from':'苏州','to':'南京','date':(TODAY+timedelta(days=3)).isoformat()},{'segment_id':'s3','from':'南京','to':'上海','date':(TODAY+timedelta(days=4)).isoformat(),'return_leg':True}];timings=[]
  for n in range(3):
   for mode in (['serial','parallel'] if n%2==0 else ['parallel','serial']):
    start=time.perf_counter()
    if mode=='parallel':data=await asyncio.gather(*(transport_segment(s,'train',leg) for leg in legs))
    else:data=[await transport_segment(s,'train',leg) for leg in legs]
    timings.append({'round':n+1,'mode':mode,'seconds':round(time.perf_counter()-start,4),'statuses':[x.get('status') for x in data],'candidates':[len(x['options']) for x in data],'candidate_ids':[[o['option_id'] for o in x['options']] for x in data]})
  out['rail_same_3_legs']=timings
  query='苏州古典园林有哪些，网师园有什么特点';cache=[]
  for n in range(3):
   # 相同输入，删除该键以区分冷缓存与热缓存；索引不重建。
   import hashlib
   key='kg:rag:'+hashlib.sha256(json.dumps([s.knowledge.version,query,'苏州',3,'none',False],ensure_ascii=False).encode()).hexdigest();await s.knowledge.redis.delete(key)
   for phase in ('cold','warm'):
    start=time.perf_counter();r=await s.knowledge.search(query,'苏州',model=None,strategy='none',rerank=False)
    cache.append({'round':n+1,'phase':phase,'seconds':round(time.perf_counter()-start,5),'cache_hit':r['cache_hit'],'ids':[r['id'] for r in r['results']]})
  out['rag_cache']=cache;Path('reports/full_benchmarks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('benchmarks saved',flush=True)
if __name__=='__main__':asyncio.run(main())
