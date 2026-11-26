"""固定题集：同输入BM25/RRF/重排比较、真实回答与Verifier，逐行保存失败。"""
import asyncio,argparse,json,hashlib,time,re,inspect
from pathlib import Path
from app.config import Settings
from app.deps import build_container
from app.retrieval.hybrid import HybridRetriever
from app.llm.usage import request_usage

def norm(s):return re.sub(r'[\s，。,:：;；()（）‑-]','',str(s)).lower()
class IdentityRank:
 async def rerank(self,query,candidates,top_k=5):return candidates[:top_k]

def rank_metrics(hits,relevant):
 ids=[h.get('_id',h.get('id'))for h in hits];ranks=[i+1 for i,id_ in enumerate(ids)if id_ in relevant]
 return {'hit_at_5':bool(ranks),'recall_at_5':len(set(ids)&relevant)/len(relevant)if relevant else None,'mrr':1/min(ranks)if ranks else 0,'retrieved_ids':ids}

async def evaluate(dataset,output,answers=True):
 c=build_container(Settings());await c.mongo.connect();await c.session_store.connect()
 cases=json.loads(dataset.read_text());chunks=await c.store.list_active_chunks();docs={d['_id']:d for d in await c.store.list_documents(status='active')}
 raw=HybridRetriever(c.bm25,c.vector_store,IdentityRank(),top_k=5,store=c.store)
 semaphore=asyncio.Semaphore(3);rows=[]
 @request_usage
 async def one(case):
  async with semaphore:
   start=time.monotonic();dept=case['dept_id'];anchor=case.get('evidence_anchor');files=set(case['relevant_files'])
   relevant={ch['_id']for ch in chunks if (docs[ch['doc_id']].get('source')or{}).get('file_name')in files and anchor and norm(anchor)in norm(ch['content'])}
   result={'id':case['id'],'query':case['query'],'answerable':case['answerable'],'relevant_chunk_ids':sorted(relevant),'label_error':case['answerable']and not relevant}
   try:
    bm=c.bm25.search(case['query'],top_k=20,dept_id=dept)
    if inspect.isawaitable(bm):bm=await bm
    bm=[h for h in bm if h.get('doc_id')in docs and 'student'in docs[h['doc_id']].get('access_roles',['student'])][:5]
    vec=await c.embeddings.embed_query(case['query'])
    rrf=await raw.retrieve(case['query'],vec,dept_id=dept)
    ranked=await c.hybrid.retrieve(case['query'],vec,dept_id=dept) if hasattr(c,'hybrid')else await c.retrieval_agent.hybrid.retrieve(case['query'],vec,dept_id=dept)
    result['retrieval']={name:rank_metrics(hits,relevant)for name,hits in [('bm25',bm),('rrf',rrf),('rerank',ranked)]}
    if answers:
     rules=await c.rule_engine.active_rules([dept]);answer=await c.orchestrator.answer_agent.generate(case['query'],ranked,rules=rules)
     verdict=await c.orchestrator.verifier_agent.verify(case['query'],answer,ranked)
     terms=case.get('expected_terms')or[];covered=[t for t in terms if norm(t)in norm(answer.content)]
     valid=0
     for citation in answer.citations:
      source=await c.store.get('chunks',f'{citation.doc_id}:{citation.chunk_index}');doc=docs.get(citation.doc_id)
      if source and doc and 'student'in doc.get('access_roles',['student']) and citation.snippet in source['content']:valid+=1
     marks=[int(n)for n in re.findall(r'\[来源(\d+)\]',answer.content)]
     result.update(answer=answer.content,verification=verdict.to_dict(),keypoint_coverage=len(covered)/len(terms)if terms else None,covered_terms=covered,missing_terms=[t for t in terms if t not in covered],citation_source_validity=valid/len(answer.citations)if answer.citations else None,inline_citation_binding=bool(marks)and all(1<=n<=len(answer.citations)for n in marks),refused=any(t in answer.content for t in ['未找到','没有明确','未明确','未提及','无法确定','未提供','无明确']))
    route=await c.orchestrator.dept_router.route(case['query']);result['route']=route;result['route_contains_expected']=dept in route['dept_ids']
   except Exception as exc:result['error']={'type':type(exc).__name__,'message':str(exc)[:200]}
   result['elapsed_seconds']=round(time.monotonic()-start,4)
   return result
 def persist():
  report={'dataset_sha256':hashlib.sha256(dataset.read_bytes()).hexdigest(),'dataset':str(dataset),'total_cases':len(cases),'completed_cases':len(rows),'rows':sorted(rows,key=lambda r:r['id']),'scope':'7份样例，助手依据源条款标注；非独立人工QA准确率；回答直接生成并另行判分，不以原文降级覆盖生成失败'}
  if len(rows)==len(cases):
   positive=[r for r in rows if r['answerable']];negative=[r for r in rows if not r['answerable']]
   report['summary']={'label_errors':sum(bool(r['label_error'])for r in rows),'errors':sum('error'in r for r in rows),'retrieval':{mode:{metric:sum((r.get('retrieval',{}).get(mode,{}).get(metric)or 0)for r in positive)/len(positive)for metric in ['hit_at_5','recall_at_5','mrr']}for mode in ['bm25','rrf','rerank']},'keypoint_coverage':sum(r.get('keypoint_coverage')or 0 for r in positive)/len(positive)if answers else None,'verifier_pass_rate':sum((r.get('verification')or{}).get('passed',False)for r in rows)/len(rows)if answers else None,'refusal_recall':sum(r.get('refused',False)for r in negative)/len(negative)if answers and negative else None,'cost_yuan':None}
  output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str))
 try:
  tasks=[asyncio.create_task(one(case))for case in cases]
  for task in asyncio.as_completed(tasks):
   result=await task;rows.append(result);persist();print(json.dumps({'completed':len(rows),'id':result['id'],'error':result.get('error'),'label_error':result['label_error']},ensure_ascii=False),flush=True)
 finally:
  for task in locals().get('tasks',[]):
   if not task.done():task.cancel()
  await asyncio.gather(*locals().get('tasks',[]),return_exceptions=True)
  await c.session_store.close();await c.mongo.close();await c.vector_store.close();await c.pi_runtime.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,default=Path('evaluation/frozen_document_qa.json'));p.add_argument('--output',type=Path,default=Path('../reports/frozen-evaluation.json'));p.add_argument('--retrieval-only',action='store_true');a=p.parse_args();asyncio.run(evaluate(a.dataset,a.output,not a.retrieval_only))
