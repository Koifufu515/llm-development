import asyncio,json,time,statistics
from pathlib import Path
from app.full.knowledge import AdvancedKnowledge
from app.utils.llm_factory import get_deepseek_llm
from app.config import Settings
CASES=[('苏州','古典园林有哪些，网师园有什么特点',['Master','Nets']),('北京','故宫是什么地方，有哪些历史背景',['Forbidden','Palace']),('上海','外滩有什么值得参观的建筑',['Bund']),('西安','秦始皇兵马俑是什么，有什么看点',['Terracotta']),('杭州','西湖有什么景点',['West Lake']),('南京','中山陵有哪些特点',['Sun Yat','Mausoleum'])]
async def main():
 k=AdvancedKnowledge();results=[]
 try:
  await k.load();model=get_deepseek_llm(Settings())
  for strategy,rerank in [('none',False),('multiquery',True)]:
   for city,q,terms in CASES:
    start=time.perf_counter();r=await k.search(q,city,k=5,model=model,strategy=strategy,rerank=rerank,use_cache=False)
    ranks=[i+1 for i,d in enumerate(r['results']) if any(t.lower() in d['text'].lower() for t in terms)]
    results.append({'city':city,'query':q,'strategy':strategy,'rerank':rerank,'seconds':round(time.perf_counter()-start,3),'found':bool(ranks),'reciprocal_rank':1/min(ranks) if ranks else 0,'city_isolation':all(d['city']==city for d in r['results']),'sources':[d['source_url'] for d in r['results']]});print(city,strategy,bool(ranks),flush=True)
  Path('reports/full_rag_diagnostic.json').write_text(json.dumps({'scope':'6条人工编写的景点实体诊断，词项命中代理指标，不是独立大样本问答准确率','results':results},ensure_ascii=False,indent=2))
 finally:await k.close()
if __name__=='__main__':asyncio.run(main())
