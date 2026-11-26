from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
TODAY=datetime.now(ZoneInfo("Asia/Shanghai")).date()
import asyncio,httpx,json,secrets,time
from pathlib import Path
async def main():
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=500,trust_env=False) as c:
  u=(await c.post('/api/v1/users/register',json={'email':'auto-'+secrets.token_hex(5)+'@kg.local','password':secrets.token_urlsafe(20)})).json();headers={'Authorization':'Bearer '+u['access_token']};report=[]
  async def run(name,req):
   cid=(await c.post('/api/v1/conversations',headers=headers,json={'title':name})).json()['id'];start=time.perf_counter()
   try:
    r=await c.post('/api/v1/conversations/'+cid+'/requirement',headers=headers,json=req)
    events=[json.loads(l[6:]) for l in r.text.splitlines() if l.startswith('data: ')]
    state=(await c.get('/api/v1/conversations/'+cid,headers=headers)).json()['state']
    row={'name':name,'seconds':round(time.perf_counter()-start,2),'conversation_id':cid,'events':events,'state':state}
    report.append(row);print(name,events[-1] if events else r.status_code,'step',state.get('current_step'),flush=True)
   except Exception as e:report.append({'name':name,'error':type(e).__name__});print(name,type(e).__name__,flush=True)
   Path('reports/full_auto_acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  common={'departure_date':(TODAY+timedelta(days=1)).isoformat(),'adult_count':1,'budget_max':6000,'auto_confirm':True}
  await run('自动多城高铁',{**common,'departure_city':'上海','destinations':['苏州','南京'],'travel_days':4,'transport_types':['train']})
  await run('自驾往返',{**common,'departure_city':'上海','destinations':['苏州'],'travel_days':2,'transport_types':['driving']})
  await run('航班往返',{**common,'departure_city':'上海','destinations':['北京'],'travel_days':2,'transport_types':['flight']})
if __name__=='__main__':asyncio.run(main())
