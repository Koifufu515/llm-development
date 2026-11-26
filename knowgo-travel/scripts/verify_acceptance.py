import asyncio,json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
async def main():
 evidence={}
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=260) as c:
  user=(await c.post('/api/users')).json()['user_id']
  await c.patch('/api/users/'+user+'/preferences',json={'pace':'轻松','travel_styles':['园林']})
  sid=(await c.post('/api/sessions',json={'user_id':user})).json()['session_id']
  day=(datetime.now(ZoneInfo('Asia/Shanghai')).date()+timedelta(days=1)).isoformat()
  body={'session_id':sid,'departure_city':'上海','departure_date':day,'stops':[{'city':'苏州','days':1}],'budget_per_person':2000,'auto_confirm':False}
  r=await c.post('/api/plans',json=body);r.raise_for_status();waiting=r.json()
  assert waiting['status']=='waiting_selection' and waiting['metrics']['llm_calls']==0
  evidence['waiting_without_generation']=True
  segment=waiting['segments'][0];assert segment['status']=='ok'
  option=next(o for o in segment['options'] if o['to_station']=='苏州' and any(s['availability']=='有' for s in o['seats']))
  payload={'session_id':sid,'revision':waiting['revision'],'option_ids':[option['option_id']]}
  endpoint='/api/plans/'+waiting['plan_id']+'/submit'
  bad=await c.post(endpoint,json={**payload,'option_ids':['foreign-option']});assert bad.status_code==422
  done=await c.post(endpoint,json=payload);done.raise_for_status();done=done.json();assert done['status']=='completed'
  assert done['selected_transport'][0]['option_id']==option['option_id']
  repeat=(await c.post(endpoint,json=payload)).json();assert repeat['plan_id']==done['plan_id']
  evidence['selection_idempotent']=True;evidence['selected_plan']=done
  changed=await c.post('/api/chat',json={'session_id':sid,'message':'把目的地改成杭州，其他不变'});changed.raise_for_status();changed=changed.json()
  assert changed['user_requirement']['destination']=='杭州' and not changed['requirement_confirmed']
  assert changed['downstream']['itinerary'] is None and not changed['planning_result']
  old=await c.post(endpoint,json=payload);assert old.status_code==409
  evidence['change_clears_and_rejects_old_submission']=True
  mem=await c.post('/api/chat',json={'session_id':sid,'message':'请长期记住我的饮食偏好：不吃辣'});mem.raise_for_status()
  prefs=(await c.get('/api/users/'+user+'/preferences')).json();assert '不吃辣' in str(prefs)
  evidence['real_agent_memory_tool']=prefs
  other=(await c.post('/api/sessions',json={'user_id':user})).json()['session_id']
  assert not (await c.get('/api/sessions/'+other)).json()['user_requirement']
  body.update({'session_id':other,'auto_confirm':True})
  events=[];result=None
  async with c.stream('POST','/api/plans/stream',json=body) as stream:
   assert stream.status_code==200
   kind=None
   async for line in stream.aiter_lines():
    if line.startswith('event: '):kind=line[7:];events.append(kind)
    if line.startswith('data: ') and kind=='result':result=json.loads(line[6:])
  assert events[-1]=='done' and 'result' in events and result['status']=='completed'
  evidence['sse_events']=events
  cancel_id=(await c.post('/api/sessions')).json()['session_id']
  async with c.stream('POST','/api/plans/stream',json={**body,'session_id':cancel_id}) as stream:
   async for line in stream.aiter_lines():
    if line.startswith('event: status'):break
  created=await c.post('/api/sessions',timeout=10);assert created.status_code==201
  evidence['disconnect_releases_write_lock']=True
 ROOT.joinpath('reports/acceptance.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 print('acceptance passed',list(evidence))
asyncio.run(main())
