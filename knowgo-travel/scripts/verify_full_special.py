from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
TODAY=datetime.now(ZoneInfo("Asia/Shanghai")).date()
import asyncio,httpx,json,secrets
from pathlib import Path
async def main():
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=500,trust_env=False) as c:
  u=(await c.post('/api/v1/users/register',json={'email':'extra-'+secrets.token_hex(5)+'@kg.local','password':secrets.token_urlsafe(18)})).json();h={'Authorization':'Bearer '+u['access_token']};out=[]
  for name,req in [('目的地含出发地',{'departure_city':'上海','destinations':['上海','苏州'],'travel_days':2,'transport_types':['driving']}),('自动推荐目的地',{'departure_city':'上海','destinations':[],'travel_days':1,'transport_types':['train'],'travel_styles':['江南古典园林'],'special_needs':'选择苏州方向的近郊城市，单日往返'})]:
   cid=(await c.post('/api/v1/conversations',headers=h,json={'title':name})).json()['id']
   r=await c.post('/api/v1/conversations/'+cid+'/requirement',headers=h,json={**req,'departure_date':(TODAY+timedelta(days=1)).isoformat(),'adult_count':1,'budget_max':3000,'auto_confirm':True})
   ev=[json.loads(l[6:]) for l in r.text.splitlines() if l.startswith('data: ')];state=(await c.get('/api/v1/conversations/'+cid,headers=h)).json()['state']
   out.append({'name':name,'events':ev,'state':state});Path('reports/full_extra_scenarios.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(name,ev[-1] if ev else r.status_code,flush=True)
if __name__=='__main__':asyncio.run(main())
