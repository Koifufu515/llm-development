import asyncio,json,statistics,sys
from datetime import datetime,timedelta
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import httpx
from app.mcp_core.client import ProjectMCPManager
from app.services.providers import query_rail,collect_queries
from app.config import Settings
from app.core.telemetry import RequestMetrics
from app.utils.llm_factory import get_deepseek_llm
from langchain_core.messages import SystemMessage,HumanMessage
from app.core.rail import compact_tickets,content_text

def summary(rows):
 ok=[r['seconds'] for r in rows if r.get('ok')]
 return {'attempted':len(rows),'succeeded':len(ok),'median_seconds':statistics.median(ok) if ok else None,'rows':rows}

async def rail_bench():
 manager=ProjectMCPManager();await manager.load_service('rail')
 tomorrow=(datetime.now(ZoneInfo('Asia/Shanghai')).date()+timedelta(days=1)).isoformat()
 legs=[{'leg_id':str(i),'fromStation':a,'toStation':b,'date':tomorrow} for i,(a,b) in enumerate([('上海','苏州'),('苏州','杭州'),('杭州','南京')])]
 results={}
 for parallel in [False,True]:
  rows=[]
  for _ in range(3):
   t=perf_counter();data=await collect_queries([(l['leg_id'],lambda l=l:query_rail(manager,l)) for l in legs],parallel)
   rows.append({'seconds':perf_counter()-t,'ok':all(x['status']=='ok' for x in data.values()),'statuses':{k:v['status'] for k,v in data.items()}})
  results['parallel' if parallel else 'serial']=summary(rows)
 return {'description':'同日三段高铁、各3轮、每调用为短stdio会话、无缓存；失败计入attempted，成功耗时另算中位数','legs':legs,**results}

async def planning_bench():
 results={}
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=260) as c:
  for mode in ['sequential','fast']:
   rows=[]
   for _ in range(3):
    session=(await c.post('/api/sessions')).json()['session_id']
    body={'session_id':session,'departure_city':'上海','departure_date':(datetime.now(ZoneInfo('Asia/Shanghai')).date()+timedelta(days=1)).isoformat(),'stops':[{'city':'苏州','days':3}],'budget_per_person':2000,'auto_confirm':True,'mode':mode}
    t=perf_counter()
    try:
     r=await c.post('/api/plans',json=body);r.raise_for_status();result=r.json()
     rows.append({'seconds':perf_counter()-t,'ok':result['status']=='completed','metrics':result['metrics'],'stages':result['stages'],'plan_id':result['plan_id'],'days':len(result['itinerary']['days'])})
    except Exception as exc:rows.append({'seconds':perf_counter()-t,'ok':False,'error':type(exc).__name__})
   results[mode]=summary(rows)
 return {'description':'单城苏州3天、各3轮；参考通道串行采集+逐日生成；快速通道并行采集+集中生成；非旧线上系统对照。各轮新会话，知识库查询缓存可能命中，记录阶段耗时。',**results}

async def token_bench():
 rawpath=ROOT/'data/samples/rail_raw_2026-10-27.json'
 if not rawpath.exists():return {'status':'unavailable','message':'原始样本不存在'}
 raw=rawpath.read_text();rows=json.loads(raw)
 if isinstance(rows,dict) and 'result' in rows:
  raw=content_text(rows['result']);rows=json.loads(raw)
 # 仅使用已留存的实际返回，不把过期班次当成当前余票展示。
 if not isinstance(rows,list):return {'status':'unavailable','message':'原始文件不是数组'}
 first=rows[0];query={'date':first['start_date'],'fromStation':'上海','toStation':'苏州'}
 compact=compact_tickets(raw,query);compacttext=json.dumps(compact,ensure_ascii=False)
 results={}
 for name,text in [('raw',raw),('compact',compacttext)]:
  samples=[]
  for _ in range(2):
   m=RequestMetrics();t=perf_counter()
   try:
    await get_deepseek_llm(Settings()).ainvoke([SystemMessage(content='这是测量工具输入Token的实验。只回复OK，不分析数据。'),HumanMessage(content=text)],config={'callbacks':[m]})
    samples.append({'ok':True,'seconds':perf_counter()-t,'metrics':m.snapshot()})
   except Exception as exc:samples.append({'ok':False,'seconds':perf_counter()-t,'error':type(exc).__name__})
  results[name]={'characters':len(text),'rows':samples}
 return {'description':'留存上海苏州真实车票JSON；两组提示词相同，API返回input_tokens；裁剪损失其余候选，不代表信息无损。',**results}

async def main():
 # 独立保存阶段结果，避免外部服务失败丢失已测证据。
 path=ROOT/'reports/performance_benchmark.json'
 out=json.loads(path.read_text()) if path.exists() else {}
 settings=Settings();out['provider']=settings.model_provider;out['model']=settings.qwen_model if settings.model_provider=='qwen' else settings.deepseek_model
 for name,fn in [('rail',rail_bench),('planning',planning_bench),('tokens',token_bench)]:
  if len(sys.argv)>1 and name not in sys.argv[1:]:continue
  try:out[name]=await fn()
  except Exception as exc:out[name]={'status':'failed','error':type(exc).__name__}
  (ROOT/'reports/performance_benchmark.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(name,'saved',flush=True)
 print('performance benchmark complete')
asyncio.run(main())
