import asyncio,json,time
from pathlib import Path
from deepeval.test_case import LLMTestCase
from evaluation.router_cases import CASES
from evaluation.router_metric import RouterCorrectnessMetric
from app.full.reference_router import chat_route
from app.utils.llm_factory import get_deepseek_llm
from app.config import Settings
async def main():
 model=get_deepseek_llm(Settings());rows=[]
 for index,case in enumerate(CASES):
  start=time.perf_counter();row={'index':index,'message':case.msg,'history':case.history,'expected_planning':case.planning,'expected_skills_any':case.skills,'expect_empty_skills':case.expect_empty_skills}
  try:
   actual=await chat_route(model,case.msg,case.history)
   metric=RouterCorrectnessMetric(case.planning,case.skills,case.expect_empty_skills)
   score=metric.measure(LLMTestCase(input=case.msg,actual_output=actual.model_dump_json()))
   row.update({'actual':actual.model_dump(),'score':score,'reason':metric.reason})
  except Exception as exc:row.update({'score':0,'error':type(exc).__name__})
  row['seconds']=time.perf_counter()-start;rows.append(row)
  Path('reports/reference-router-after.json').write_text(json.dumps({'scope':'原0650全部路由样本；真实Qwen输出，用原确定性RouterCorrectnessMetric评分，不调用LLM作裁判。','model':model.model_name,'rows':rows},ensure_ascii=False,indent=2));print(index,case.note,row['score'],row.get('error',''),flush=True)
asyncio.run(main())
