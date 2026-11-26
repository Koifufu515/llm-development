"""在线/离线共用DeepEval标尺；在线结果是异步告警，不伪装成事实真值。"""
import asyncio,json,os
from sqlalchemy import select
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.full.database import Plan

class QwenJudge:
    """工厂返回当前安装版本要求的DeepEvalBaseLLM适配器。"""
    @staticmethod
    def create(model):
        from deepeval.models import DeepEvalBaseLLM
        class Judge(DeepEvalBaseLLM):
            def __init__(self):super().__init__(model_name='QwenJudge')
            def load_model(self):return model
            def get_model_name(self):return 'QwenJudge'
            def generate(self,prompt,schema=None,**kwargs):
                return asyncio.run(self.a_generate(prompt,schema,**kwargs))
            async def a_generate(self,prompt,schema=None,**kwargs):
                if schema:
                    return await model.with_structured_output(schema,method='function_calling').ainvoke(prompt)
                return str((await model.ainvoke(prompt)).content)
        return Judge()

def build_evidence_metrics(model):
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCaseParams
    judge=QwenJudge.create(model)
    rules=[('完整性','核对要求的天数、城市、交通、住宿和各时段是否完整。交通占据时段可接受，不要求到达前安排景点。'),
           ('需求匹配','核对预算、风格、人数、餐饮和长期禁忌。明确估算允许存在，但不能违反已确认约束。'),
           ('资料一致性','只按提供的完整来源记录（含id/正文/URL）与候选核对事实。source_ids须在记录id中查找。行程拟定时间、合理提醒属于规划建议，不是营业事实；具体开放时间、地址、交通时刻、入住承诺必须有证据，不以常识补证。未核实的建议应明示待核实。')]
    steps={
      '完整性':['从Input提取明确要求的天数、目的地、人数与交通住宿约束。','按确认日期拓扑核对四时段覆盖、已选各交通段和有住宿夜晚的酒店。','一日游不要求住宿；目的地含出发城市、本地游均合法；交通占据时段和返程后休息均合法，不强迫景点。','只对缺失的必要内容扣分，不为未要求的模块扣分。'],
      '需求匹配':['逐项核对Input已明确预算、风格、餐饮、人数与长期禁忌。','已确认交通、住宿优先，以Context中候选和账本为准；估算不当已订价格。','对违反明确需求的安排扣分，不臆造额外需求。'],
      '资料一致性':['先区分拟定行程时段和供应商/景点事实，拟定活动时间不是营业事实，不因时段无来源扣分。','攻略source_ids在Context完整来源记录的id字段查找；交通和酒店使用独立候选，不能要求它们引用攻略id。','核对具体地址、历史、门票、预约和营业事实是否在Context中；仅看资料标题或常识不能算支持。','未经支持的具体事实应扣分；明确待核实的建议不当作已确认事实，但不能与候选已知事实相矛盾。']}
    return [GEval(name=name,criteria=criteria,evaluation_steps=steps[name],evaluation_params=[LLMTestCaseParams.INPUT,LLMTestCaseParams.ACTUAL_OUTPUT,LLMTestCaseParams.CONTEXT],model=judge,threshold=.7,async_mode=True) for name,criteria in rules]


def build_itinerary_metrics(model,threshold=.5,require_budget=True):
    from app.full.reference_quality import build_itinerary_metrics as original_factory
    return original_factory(model,threshold,require_budget)


async def evaluate(model,requirement,body,transport,sources):
    from deepeval.test_case import LLMTestCase
    costs=requirement.get('budget')
    if costs:
        from app.full.plans import render
        text=render(body,costs,sources)
    else:
        lines=['# '+body.get('title','旅行行程')]
        for day in body['days']:
            lines.append('## Day '+str(day['day'])+' '+day['city'])
            for slot,label in [('morning','上午'),('noon','中午'),('afternoon','下午'),('evening','晚上')]:
                lines.append('**'+label+'**')
                lines.extend('- '+a['description'] for a in day[slot])
            lines.append('小贴士：'+'；'.join(day['tips']))
        text='\n'.join(lines)
    case=LLMTestCase(input=json.dumps(requirement,ensure_ascii=False),actual_output=text,
       context=[json.dumps(transport,ensure_ascii=False),*[json.dumps(row,ensure_ascii=False) for row in sources]])
    results=[]
    for metric in build_itinerary_metrics(model,require_budget=bool(costs)):
        await metric.a_measure(case)
        results.append({'name':metric.name,'score':metric.score,'reason':metric.reason,'threshold':.5})
    return {'status':'warning' if any(r['score']<.5 for r in results) else 'passed','metrics':results,
            'scope':'原文三维GEval裁判评分（真实性基于模型常识，不是官方事实核验），不等同事实准确率；不阻断主流程。'}

def schedule_quality(services,plan_id,req,body,transport,sources,hotels=None,costs=None,memory=None,revision=None):
    async def run():
        try:result=await asyncio.wait_for(evaluate(services.model,{**req.model_dump(mode='json'),'budget':costs,'memory':memory},body,[*transport,*(hotels or [])],sources),180)
        except Exception as exc:result={'status':'unavailable','reason':type(exc).__name__,'scope':'裁判失败不影响已保存行程'}
        async with services.db.session() as db:
            row=await db.get(Plan,plan_id)
            if row and (revision is None or row.revision==revision):
                row.quality=result;await db.commit()
    import contextvars
    from langchain_core.runnables.config import var_child_runnable_config
    context=contextvars.copy_context()
    context.run(var_child_runnable_config.set,None)
    task=asyncio.create_task(run(),context=context);services.tasks.add(task);task.add_done_callback(services.tasks.discard)
