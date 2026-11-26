"""原0655六样本×2轮，共享线上原三维工厂；保存逐次得分、耗时和错误。"""
import asyncio,json,time,statistics,os
from pathlib import Path
from deepeval.test_case import LLMTestCase
from app.full.reference_quality import build_itinerary_metrics
from app.utils.llm_factory import get_deepseek_llm
from app.config import Settings
from evaluation.itinerary_cases import ITINERARY_CASES
async def main():
 model=get_deepseek_llm(Settings());records=[];sem=asyncio.Semaphore(2)
 stable=os.getenv('REFERENCE_STABLE_STEPS')=='1'
 output=Path('reports/reference-six-cases-stable.json' if stable else 'reports/reference-six-cases.json')
 def save():
  output.write_text(json.dumps({'scope':'原0655固定六样本，三正三反，两次独立评分；原三维GEval阈值0.5。模型裁判识别率不是事实准确率。','model':model.model_name,'stable_steps':stable,'records':records},ensure_ascii=False,indent=2))
 async def run(index,case,repeat):
  async with sem:
   row={'case_index':index,'note':case['note'],'positive':case['positive'],'repeat':repeat,'metrics':[]};records.append(row)
   tc=LLMTestCase(input=case['input'],actual_output=case['actual_output'])
   for metric in build_itinerary_metrics(model,stable_steps=stable):
    start=time.perf_counter()
    try:
     await asyncio.wait_for(metric.a_measure(tc),120)
     row['metrics'].append({'name':metric.name,'score':metric.score,'threshold':metric.threshold,'passed':metric.is_successful(),'reason':metric.reason,'seconds':time.perf_counter()-start})
    except Exception as exc:row['metrics'].append({'name':metric.name,'error':type(exc).__name__,'message':str(exc)[:250],'seconds':time.perf_counter()-start})
    save();print(index,repeat,metric.name,row['metrics'][-1].get('score',row['metrics'][-1].get('error')),flush=True)
   valid=all('score' in m for m in row['metrics'])
   row['classified_positive']=all(m.get('passed',False) for m in row['metrics']) if valid else None
   row['correct']=row['classified_positive']==row['positive'] if valid else None
   save()
 await asyncio.gather(*(run(i,c,r) for r in (1,2) for i,c in enumerate(ITINERARY_CASES)))
 print('evaluated',len(records),'recognized',sum(r['correct'] is True for r in records),'errors',sum(r['correct'] is None for r in records))
asyncio.run(main())
