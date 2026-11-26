import asyncio,json,time
from pathlib import Path
from app.full.knowledge import AdvancedKnowledge
from app.utils.llm_factory import get_deepseek_llm
from app.config import Settings
from app.core.telemetry import RequestMetrics
from langchain_core.runnables.config import var_child_runnable_config
async def main():
 k=AdvancedKnowledge();await k.load();model=get_deepseek_llm(Settings());rows=[]
 try:
  seed=await k.search('苏州园林和博物馆游览推荐','苏州',model=model)
  for repeat in range(1,4):
   await k.redis.delete(seed['cache_key'])
   pair={}
   for mode in ('cold','warm'):
    metrics=RequestMetrics();token=var_child_runnable_config.set({'callbacks':[metrics]});start=time.perf_counter()
    try:result=await k.search('苏州园林和博物馆游览推荐','苏州',model=model)
    finally:var_child_runnable_config.reset(token)
    pair[mode]={'seconds':time.perf_counter()-start,'cache_hit':result['cache_hit'],'ids':[r['id'] for r in result['results']],'queries':result['queries'],'pipeline':result['pipeline'],'model':result['reranker_model'],'metrics':metrics.snapshot(),'pipeline_complete':result['pipeline_complete'],'rerank_scores':result['rerank_scores'],'query_error':result['query_error'],'rerank_error':result['rerank_error'],'failures':result['llm_failures']}
   rows.append({'repeat':repeat,**pair,'same_ids':pair['cold']['ids']==pair['warm']['ids']})
   Path('reports/reference-rag-cold-warm.json').write_text(json.dumps({'scope':'同城同查询/同模型/同管线；冷时只清本查询Redis键，计入真实查询优化与LLM重排，索引已加载；预热一次后各3轮。','corpus':k.status,'rows':rows},ensure_ascii=False,indent=2));print(repeat,pair['cold']['seconds'],pair['warm']['seconds'],pair['cold']['cache_hit'],pair['warm']['cache_hit'],flush=True)
 finally:await k.close()
asyncio.run(main())
