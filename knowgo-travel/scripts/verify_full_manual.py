import asyncio,httpx,json,secrets
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
async def main():
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',timeout=500,trust_env=False) as c:
  r=await c.post('/api/v1/users/register',json={'email':'manual-'+secrets.token_hex(5)+'@kg.local','password':secrets.token_urlsafe(15)});r.raise_for_status();h={'Authorization':'Bearer '+r.json()['access_token']}
  cid=(await c.post('/api/v1/conversations',headers=h,json={})).json()['id'];log=[]
  async def send(path,body):
   r=await c.post(path,headers=h,json=body);r.raise_for_status()
   ev=[json.loads(l[6:]) for l in r.text.splitlines() if l.startswith('data: ')];log.append({'path':path,'events':ev});print(path,[e['role'] for e in ev],flush=True)
   if not ev or ev[-1].get('code')!=200:raise ValueError(str(ev)[-1800:])
   return ev
  req={'departure_city':'上海','destinations':['苏州'],'departure_date':(datetime.now(ZoneInfo('Asia/Shanghai')).date()+timedelta(days=1)).isoformat(),'travel_days':2,'adult_count':1,'budget_max':3000,'auto_confirm':False}
  try:
   await send('/api/v1/conversations/'+cid+'/requirement',req)
   events=await send('/api/v1/messages',{'conversation_id':cid,'content':'确认'})
   for n in range(2):
    card=next(e['content'] for e in events if e['role']=='skill_ui');choices=[]
    for segment in card['data']['segments']:
     opts=segment['options']
     if card['data']['mode']=='train':opts=[o for o in opts if o['availability'] in ('有','有票') or str(o['availability']).isdigit() and int(o['availability'])>0]
     if opts:choices.append({'segment_id':segment['segment_id'],'option_id':opts[0]['option_id']})
    if n==0:transport_receipt={'conversation_id':cid,'card_id':card['id'],'revision':card['revision'],'selections':choices,'skill_name':card['skill_name']}
    events=await send('/api/v1/skills/'+card['skill_name']+'/submit',{'conversation_id':cid,'card_id':card['id'],'revision':card['revision'],'selections':choices})
   state=(await c.get('/api/v1/conversations/'+cid,headers=h)).json()['state'];print('final',state['current_step'],state.get('plan_id'),flush=True)
   repeat=await send('/api/v1/skills/'+transport_receipt.pop('skill_name')+'/submit',transport_receipt)
   changed={**req,'destinations':['杭州']}
   await send('/api/v1/conversations/'+cid+'/requirement',changed)
   stale=await c.post('/api/v1/skills/train_multi_segment/submit',headers=h,json=transport_receipt)
   oldplan=(await c.get('/api/v1/plans/'+state['plan_id'],headers=h)).json()
   log.append({'idempotent':any(e['role']=='assistant' and '无需重复' in e['content'] for e in repeat),'stale_after_change':stale.status_code,'old_plan_marked_stale':oldplan.get('is_current') is False})
  finally:Path('reports/full_manual_chain.json').write_text(json.dumps({'conversation_id':cid,'rounds':log},ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
