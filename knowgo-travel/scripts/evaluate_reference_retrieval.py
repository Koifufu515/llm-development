"""冻结18问检索验证：开发期6城与本集分离。助手按原来源实体标注，未经独立人工复核。
比较同一3120子块/654父块上的基础RRF与完整MultiQuery+LLM重排，非问答准确率。
"""
import asyncio,json,time,hashlib
from pathlib import Path
from app.full.knowledge import AdvancedKnowledge
from app.config import Settings
from app.utils.llm_factory import get_deepseek_llm
async def main():
    source=Path('reports/full_rag_validation_set.json');data=json.loads(source.read_text());kb=AdvancedKnowledge();await kb.load();model=get_deepseek_llm(Settings());rows=[]
    def save():
        aggregate={}
        for mode in ('rrf','full'):
            group=[r for r in rows if r['mode']==mode]
            if group:aggregate[mode]={'n':len(group),'recall_at_3':sum(r['recall_at_3'] for r in group)/len(group),'hit_at_3':sum(r['hit_at_3'] for r in group)/len(group),'mrr_at_3':sum(r['mrr_at_3'] for r in group)/len(group),'errors':sum('error' in r for r in group),'pipeline_failures':sum(not r.get('pipeline_complete',False) for r in group)}
        Path('reports/reference-retrieval.json').write_text(json.dumps({'scope':__doc__,'dataset_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'corpus':kb.status,'aggregate':aggregate,'rows':rows},ensure_ascii=False,indent=2))
    try:
        for index,case in enumerate(data['cases']):
            relevant=set(case['relevant_parent_ids'])
            for mode in ('rrf','full'):
                row={'index':index,'city':case['city'],'query':case['query'],'mode':mode,'relevant_parent_ids':sorted(relevant),'recall_at_3':0.0,'hit_at_3':False,'mrr_at_3':0.0};start=time.perf_counter()
                try:
                    result=await kb.search(case['query'],case['city'],k=3,model=model if mode=='full' else None,strategy='multiquery' if mode=='full' else 'none',rerank=mode=='full',use_cache=False)
                    ids=[x['id'] for x in result['results']];hits=relevant.intersection(ids)
                    row.update({'returned_parent_ids':ids,'recall_at_3':len(hits)/len(relevant),'hit_at_3':bool(hits),'mrr_at_3':next((1/(i+1) for i,pid in enumerate(ids) if pid in relevant),0.0),'pipeline_complete':result.get('pipeline_complete',True),'query_error':result.get('query_error'),'rerank_error':result.get('rerank_error')})
                except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)[:180]
                row['seconds']=time.perf_counter()-start;rows.append(row);save()
            print(index+1,case['city'],[(r['mode'],r['hit_at_3'])for r in rows[-2:]],flush=True)
    finally:await kb.close()
asyncio.run(main())
