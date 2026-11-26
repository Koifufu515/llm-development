import asyncio,json
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import httpx
async def main():
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=260) as c:
  user=(await c.post('/api/users')).json()['user_id']
  r=await c.patch('/api/users/'+user+'/preferences',json={'pace':'轻松','travel_styles':['园林']});r.raise_for_status()
  session=(await c.post('/api/sessions',json={'user_id':user})).json()['session_id']
  body={'session_id':session,'departure_city':'上海','departure_date':(datetime.now(ZoneInfo('Asia/Shanghai')).date()+timedelta(days=1)).isoformat(),'stops':[{'city':'苏州','days':3}],'budget_per_person':2000,'auto_confirm':True}
  r=await c.post('/api/plans',json=body)
  print('plan_http',r.status_code)
  if r.status_code!=200:print(r.text[:300]);return
  result=r.json();assert result['status']=='completed' and len(result['itinerary']['days'])==3
  saved=(await c.get('/api/sessions/'+session)).json()
  assert saved['current_step']=='report_generation' and saved['downstream']['budget']
  plans=(await c.get('/api/sessions/'+session+'/plans')).json();assert plans['plans']
  other=(await c.post('/api/sessions',json={'user_id':user})).json()['session_id']
  assert not (await c.get('/api/sessions/'+other)).json()['user_requirement']
  assert (await c.get('/api/users/'+user+'/preferences')).json()['pace']=='轻松'
  evidence={'scenario':'真实DeepSeek+PG+12306/Open-Meteo+本地BGE，单城3天','result':result,'restored_state':saved,'new_session_isolated':True,'cross_session_preferences':True}
  Path('reports/live_delivery.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
  print(json.dumps({'status':result['status'],'metrics':result['metrics'],'stages':result['stages'],'rail_status':[x['status'] for x in result['segments']]},ensure_ascii=False))
asyncio.run(main())
