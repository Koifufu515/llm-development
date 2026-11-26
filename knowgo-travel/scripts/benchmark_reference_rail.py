import asyncio,json,time,statistics
from pathlib import Path
from types import SimpleNamespace
from app.mcp_core.client import ProjectMCPManager
from app.full.capabilities import transport_segment
from app.full.rail_guard import compact_ticket_text,parse_ticket_rows
from app.core.rail import content_text
async def main():
 m=ProjectMCPManager();await m.load_service('rail');s=SimpleNamespace(mcp_manager=m)
 tool=next(t for t in m.tools['rail'] if t.name=='get-tickets')
 raw=await tool.ainvoke({'date':'2026-11-01','fromStation':'上海','toStation':'苏州','format':'text','limitedNum':0,'trainFilterFlags':'GD'})
 text=content_text(raw);packed=compact_ticket_text(raw)
 crop={'date':'2026-11-01','route':'上海→苏州','raw_characters':len(text),'raw_trains':len(parse_ticket_rows(raw)),'compact_characters':len(packed),'compact_trains':len(parse_ticket_rows(raw)[:12]),'compact_text':packed}
 Path('reports/reference-rail-raw.txt').write_text(text)
 legs=[{'segment_id':'s1','from':'上海','to':'苏州','date':'2026-11-01'},{'segment_id':'s2','from':'苏州','to':'杭州','date':'2026-11-02'},{'segment_id':'s3','from':'杭州','to':'上海','date':'2026-11-03'}];rows=[]
 for repeat in range(1,4):
  measurements={}
  # 交替先后顺序，避免始终把首次连接开销归于同一组。
  for mode in (('serial','parallel') if repeat%2 else ('parallel','serial')):
   start=time.perf_counter()
   if mode=='serial':results=[await transport_segment(s,'train',leg) for leg in legs]
   else:results=await asyncio.gather(*(transport_segment(s,'train',leg) for leg in legs))
   measurements[mode]={'seconds':time.perf_counter()-start,'successes':sum(bool(r.get('options')) for r in results),'option_counts':[len(r.get('options',[])) for r in results]}
  rows.append({'repeat':repeat,**measurements})
  Path('reports/reference-rail-benchmark.json').write_text(json.dumps({'scope':'同三段/日期/过滤参数，串并行各3轮，交替顺序，含真实MCP请求，不代表线上吞吐。','crop':crop,'legs':legs,'rows':rows},ensure_ascii=False,indent=2));print(repeat,measurements,flush=True)
asyncio.run(main())
