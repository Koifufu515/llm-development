import asyncio,json,httpx,secrets,time
from pathlib import Path
async def main():
 rows=[]
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',trust_env=False,timeout=120) as c:
  u=(await c.post('/api/v1/users/register',json={'email':'stream-'+secrets.token_hex(5)+'@kg.local','password':secrets.token_urlsafe(18)})).json();h={'Authorization':'Bearer '+u['access_token']}
  for n in range(3):
   cid=(await c.post('/api/v1/conversations',headers=h,json={})).json()['id'];t=time.perf_counter();first=None;count=0;done=None
   async with c.stream('POST','/api/v1/messages',headers=h,json={'conversation_id':cid,'content':'你好，请简短介绍一下你能做什么。'}) as r:
    async for line in r.aiter_lines():
     if not line.startswith('data: '):continue
     e=json.loads(line[6:])
     if e['role']=='assistant' and e['content']:
      count+=1
      if first is None:first=round(time.perf_counter()-t,4)
     if e['role']=='done':done=e['code']
   messages=(await c.get('/api/v1/messages',headers=h,params={'conversation_id':cid})).json()['items'];rows.append({'round':n+1,'first_text_seconds':first,'elapsed_seconds':round(time.perf_counter()-t,4),'assistant_chunks':count,'done':done,'metrics':messages[-1]['extra'].get('metrics')})
  Path('reports/full_streaming.json').write_text(json.dumps({'scope':'同一闲聊输入，新会话，各3轮；客户端首文本块不是规划进度事件。','results':rows},ensure_ascii=False,indent=2));print(rows)
if __name__=='__main__':asyncio.run(main())
