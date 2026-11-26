"""原方案最终功能验收；复用先前真实候选，单独验证安全/状态/文字选择/历史版本。
不会把复用候选的场景计为新一轮模型质量或时延评测。
"""
import asyncio,json,secrets,copy
from pathlib import Path
from datetime import timedelta
import httpx
from sqlalchemy import select
from langgraph.graph import StateGraph,START,END
from app.config import Settings
from app.full.agent import FullState
from app.full.database import Database,Card,Plan,now
from app.full.workflow import Services
from app.core.checkpointer import open_checkpointer
async def main():
 report={'scope':__doc__,'checks':{}};out=Path('reports/reference-final-acceptance.json')
 def check(name,condition):
  report['checks'][name]=bool(condition);out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(name,bool(condition),flush=True)
  if not condition:raise AssertionError(name)
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',trust_env=False,timeout=300) as c,open_checkpointer(Settings()) as saver:
  db=Database(Settings());svc=Services.__new__(Services);svc.db=db
  builder=StateGraph(FullState);builder.add_node('read_only',lambda s:{});builder.add_edge(START,'read_only');builder.add_edge('read_only',END);svc.reader=builder.compile(checkpointer=saver)
  try:
   health=(await c.get('/health/config')).json();report['services']=health['mcp_services'];check('nine_mcp_services_discovered',sum(v=='ready' for v in health['mcp_services'].values())==9)
   username='accept-'+secrets.token_hex(5);email=username+'@kg.local';password=secrets.token_urlsafe(20)
   u=(await c.post('/api/v1/users/register',json={'username':username,'email':email,'password':password})).json();h={'Authorization':'Bearer '+u['access_token']};uid=u['user']['id']
   login=await c.post('/api/v1/users/login',json={'username':username,'password':password});check('username_login',login.status_code==200)
   check('duplicate_username_rejected',(await c.post('/api/v1/users/register',json={'username':username,'email':'other-'+email,'password':password})).status_code==409)
   check('jwt_required',(await c.get('/api/v1/conversations')).status_code==401)
   cid=(await c.post('/api/v1/conversations',headers=h,json={'title':'文字选票验收'})).json()['id']
   other=(await c.post('/api/v1/users/register',json={'email':'other-'+secrets.token_hex(5)+'@kg.local','password':password})).json();oh={'Authorization':'Bearer '+other['access_token']}
   check('conversation_foreign_404',(await c.get('/api/v1/conversations/'+cid,headers=oh)).status_code==404)
   check('anonymous_legacy_cannot_read_formal',(await c.get('/api/sessions/'+cid)).status_code==404)
   async def turn(path,payload):
    events=[]
    async with c.stream('POST',path,headers=h,json=payload) as response:
     response.raise_for_status()
     async for line in response.aiter_lines():
      if line.startswith('data: '):events.append(json.loads(line[6:]))
    check('sse_done_'+str(len(report.get('turns',[]))),bool(events and events[-1].get('code')==200))
    report.setdefault('turns',[]).append({'path':path,'roles':[e['role'] for e in events],'errors':[e for e in events if e['role']=='error']});return events
   snap=json.loads(Path('reports/reference-full-e2e.json').read_text());source=snap['state'];req={**source['requirement'],'auto_confirm':False};picked=source['selected_transport'];report['candidate_source_conversation']=snap['conversation_id']
   payload={'mode':'train','skill_name':'train_multi_segment','segments':[{**{k:p[k] for k in ('segment_id','from','to','date')},'options':[p]} for p in picked]}
   async with db.session() as session:
    card=Card(conversation_id=cid,skill_name='train_multi_segment',revision=1,payload=payload,expires_at=now()+timedelta(minutes=10));session.add(card);await session.commit();card_id=card.id
   await svc.write(cid,{'requirement':req,'revision':1,'confirmed_revision':1,'current_step':'transport_planning','selected_transport':[],'selected_hotels':[],'active_card':{'id':card_id,'skill_name':'train_multi_segment'}})
   request={'conversation_id':cid,'card_id':card_id,'revision':1,'selections':[{'segment_id':p['segment_id'],'option_id':'forged'} for p in picked]}
   check('forged_options_422',(await c.post('/api/v1/skills/train_multi_segment/submit',headers=h,json=request)).status_code==422)
   async with db.session() as session:
    row=await session.get(Card,card_id);row.expires_at=now()-timedelta(seconds=1);await session.commit()
   request['selections']=[{'segment_id':p['segment_id'],'option_id':p['option_id']} for p in picked]
   check('expired_card_409',(await c.post('/api/v1/skills/train_multi_segment/submit',headers=h,json=request)).status_code==409)
   async with db.session() as session:
    row=await session.get(Card,card_id);row.expires_at=now()+timedelta(minutes=10);await session.commit()
   for index,p in enumerate(picked):
    await turn('/api/v1/messages',{'conversation_id':cid,'content':f"确认第{index+1}段{p['from']}到{p['to']}，我选择{p['name']}，按卡片的原价和时间。"})
    state=(await c.get('/api/v1/conversations/'+cid,headers=h)).json()['state']
    check('text_select_leg_'+str(index+1),any(r['option_id']==p['option_id'] for r in state['selected_transport']))
   check('all_legs_before_hotel',state['current_step']=='accommodation_planning')
   image_events=await turn('/api/v1/messages',{'conversation_id':cid,'content':'搜索苏州拙政园图片'})
   msgs=(await c.get('/api/v1/messages',headers=h,params={'conversation_id':cid})).json()['items'];facts=msgs[-1]['extra'].get('facts',{})
   check('real_image_mcp_query',facts.get('status')=='ok' and bool(facts.get('images')))
   cid2=(await c.post('/api/v1/conversations',headers=h,json={'title':'预算多版本验收'})).json()['id']
   async with db.session() as session:
    old=Plan(conversation_id=cid2,title=snap['plan']['title'],revision=1,body=snap['plan']['body'],budget=snap['plan']['budget'],map_data=snap['plan']['map_data']);session.add(old);await session.commit();old_id=old.id
   await svc.write(cid2,{**{k:v for k,v in source.items() if k!='messages'},'user_id':uid,'requirement':req,'revision':1,'confirmed_revision':1,'current_step':'budget_summarization','plan_id':old_id})
   await turn('/api/v1/messages',{'conversation_id':cid2,'content':'只把人均预算上限改成4500元，其他都不改，请重新汇总预算。'})
   state2=(await c.get('/api/v1/conversations/'+cid2,headers=h)).json()['state'];old_json=(await c.get('/api/v1/plans/'+old_id,headers=h)).json();new_json=(await c.get('/api/v1/plans/'+state2['plan_id'],headers=h)).json()
   check('budget_change_preserves_body',state2['itinerary_body']==source['itinerary_body'])
   check('history_version_preserved',state2['plan_id']!=old_id and old_json['budget']==snap['plan']['budget'])
   check('legacy_four_layer_contract',len(new_json['plan_data']['itinerary_list'])==req['travel_days'])
   check('budget_arithmetic',round(sum(r['amount'] for r in new_json['budget']['items']),2)==new_json['budget']['total'])
   await turn('/api/v1/messages',{'conversation_id':cid2,'content':'把目的地改成杭州，其他不变，先不要查交通。'})
   changed=(await c.get('/api/v1/conversations/'+cid2,headers=h)).json()['state'];check('destination_change_clears_dependents',changed['requirement']['destinations']==['杭州'] and not changed.get('selected_transport') and changed.get('itinerary_body') is None)
   await turn('/api/v1/messages',{'conversation_id':cid2,'content':'请长期记住，我海鲜过敏，住宿偏好民宿，每晚预算400元。'})
   mem=(await c.get('/api/v1/memory',headers=h)).json();report['memory']=mem
   check('typed_memory_saved',bool(mem.get('profile',{}).get('dietary_restrictions')))
   other_mem=(await c.get('/api/v1/memory',headers=oh)).json();check('memory_user_isolation',not other_mem.get('profile',{}).get('dietary_restrictions'))
   check('soft_delete',(await c.delete('/api/v1/conversations/'+cid,headers=h)).status_code==200)
   check('deleted_404',(await c.get('/api/v1/conversations/'+cid,headers=h)).status_code==404)
   report['status']='passed';out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
  finally:await db.close()
asyncio.run(main())
