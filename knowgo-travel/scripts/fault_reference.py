"""可重复故障注入：实际LangGraph/工具/PG落库，模型协议和地图用先前真实产物回放。
不计为新Qwen质量评测或实时地图查询；验证主生成异常→标准Agent工具提交→保存。
"""
import asyncio,json,secrets,copy
from pathlib import Path
from sqlalchemy import select
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from app.main import app
from app.full.database import User,Conversation,Plan
from app.full.security import password_hash
from app.full.agent import reset_after
import app.full.workflow as workflow
class BoundFake(FakeMessagesListChatModel):
 def bind_tools(self,tools,**kwargs):return self
async def main():
 snapshot=json.loads(Path('reports/reference-full-e2e.json').read_text());report={'scope':__doc__,'source_conversation':snapshot['conversation_id'],'checks':{}}
 async with app.router.lifespan_context(app):
  s=app.state.full;source=snapshot['state'];original_generate=workflow.generate;original_map=workflow.enrich_map
  async with s.db.session() as db:
   salt=secrets.token_hex(5);u=User(username='fault-'+salt,email='fault-'+salt+'@kg.local',password_hash=await password_hash('LocalFaultDemo2026!'));db.add(u);await db.flush();conv=Conversation(user_id=u.id,title='标准回退协议故障注入');db.add(conv);await db.commit();cid=conv.id;uid=u.id
  await s.write(cid,{'messages':[],'user_id':uid,**{k:copy.deepcopy(v) for k,v in source.items() if k!='messages'},'user_id':uid,'revision':1,'confirmed_revision':1,'current_step':'itinerary_generation',**reset_after('itinerary_generation'),'itinerary_sources':source.get('itinerary_sources',[])})
  s.model=BoundFake(responses=[AIMessage(content='',tool_calls=[{'name':'submit_itinerary_body_tool','args':{'days':snapshot['plan']['body']['days']},'id':'fault-body'}])])
  async def broken(*args,**kwargs):raise ValueError('INJECTED_PRIMARY_GENERATOR_FAILURE')
  async def cached_map(*args,**kwargs):return copy.deepcopy(snapshot['plan']['map_data'])
  workflow.generate=broken;workflow.enrich_map=cached_map;events=[]
  async def emit(role,content,code=None):events.append({'role':role,'content':content})
  try:
   result=await s.advance(cid,uid,emit);state=await s.state(cid)
   async with s.db.session() as db:plan=await db.get(Plan,state['plan_id'])
   report['checks']={'fallback_skill_emitted':any(e['role']=='skills' and e['content'].get('skill_name')=='standard_fallback' for e in events),'body_saved':len(plan.body['days'])==source['requirement']['travel_days'],'terminal_step':state['current_step']=='budget_summarization','model_protocol_used':'submit_itinerary_body_tool' in [getattr(m,'name',None) for m in state.get('messages',[])],'rendered_full_budget':'预算明细' in result['text']}
   report['plan_id']=plan.id;report['status']='passed' if all(report['checks'].values()) else 'failed'
  finally:workflow.generate=original_generate;workflow.enrich_map=original_map
 Path('reports/reference-faults.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
asyncio.run(main())
