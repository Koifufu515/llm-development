import asyncio,httpx,json,secrets,time
from pathlib import Path
async def main():
 rows=[]
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',trust_env=False,timeout=90) as c:
  u=(await c.post('/api/v1/users/register',json={'email':'frame-'+secrets.token_hex(5)+'@kg.local','password':secrets.token_urlsafe(18)})).json();h={'Authorization':'Bearer '+u['access_token']}
  for repeat in range(1,4):
   for mode in ('form','chat'):
    cid=(await c.post('/api/v1/conversations',headers=h,json={'title':'首帧测试'})).json()['id']
    body={'departure_city':'上海','destinations':['苏州'],'departure_date':'2026-11-01','travel_days':3,'adult_count':1,'budget_max':5000,'auto_confirm':False}
    path=f'/api/v1/conversations/{cid}/requirement' if mode=='form' else '/api/v1/messages'
    payload=body if mode=='form' else {'conversation_id':cid,'content':'请规划从上海去苏州的旅行，2026年11月1日出发，3天，1个成人，0儿童，每人预算5000元，坐高铁，逐步确认。'}
    start=time.perf_counter()
    async with c.stream('POST',path,headers=h,json=payload) as response:
     response.raise_for_status()
     async for line in response.aiter_lines():
      if line.startswith('data: '):
       event=json.loads(line[6:]);rows.append({'repeat':repeat,'mode':mode,'seconds':time.perf_counter()-start,'first_role':event['role'],'first_text':event.get('content') if event['role']=='assistant' else None});break
    # 关闭后用同会话下一次写请求验证写锁释放，耗时单列，不纳入首帧。
    started=time.perf_counter();event_count=0
    async with c.stream('POST','/api/v1/messages',headers=h,json={'conversation_id':cid,'content':'你好'}) as response:
     async for line in response.aiter_lines():
      if line.startswith('data: '):
       event=json.loads(line[6:]);event_count+=1
       if event['role']=='done':rows[-1]['next_request_done_code']=event.get('code')
    rows[-1]['disconnect_then_next_write_seconds']=time.perf_counter()-started
    Path('reports/reference-first-frame.json').write_text(json.dumps({'scope':'同一完整旅行需求，两种输入格式；量首业务SSE帧（可能skills，非模型首Token），各3轮；读首帧主动断连，另测下一写请求解锁。','rows':rows},ensure_ascii=False,indent=2));print(rows[-1],flush=True)
asyncio.run(main())
