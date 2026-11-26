import asyncio,httpx,secrets,json,time
from pathlib import Path
BASE='http://127.0.0.1:8001'
def frames(r):return [json.loads(l[6:]) for l in r.text.splitlines() if l.startswith('data: ')]
async def main():
 out={}
 async with httpx.AsyncClient(base_url=BASE,timeout=180,trust_env=False) as c:
  email='resilience-'+secrets.token_hex(4)+'@kg.local';password=secrets.token_urlsafe(16)
  u=(await c.post('/api/v1/users/register',json={'email':email,'password':password})).json();h={'Authorization':'Bearer '+u['access_token']}
  cid=(await c.post('/api/v1/conversations',headers=h,json={'title':'恢复与记忆验证'})).json()['id']
  r=await c.post('/api/v1/messages',headers=h,json={'conversation_id':cid,'content':'请长期记住，我海鲜过敏。'})
  mem=(await c.get('/api/v1/memory',headers=h)).json();out['model_memory_events']=frames(r);out['allergy_in_correct_category']=any('海鲜' in v for v in mem.get('dietary_restrictions',[]))
  cid2=(await c.post('/api/v1/conversations',headers=h,json={'title':'跨会话'})).json()['id']
  r=await c.post('/api/v1/messages',headers=h,json={'conversation_id':cid2,'content':'我有什么饮食禁忌？'})
  out['cross_conversation_reply']=frames(r);out['cross_conversation_memory']='海鲜' in r.text
  # 补槽必须保留查票种类，不写规划需求。
  r=await c.post('/api/v1/messages',headers=h,json={'conversation_id':cid2,'content':'帮我查上海到苏州的高铁'})
  out['pending_asks_date']='日期' in r.text
  r=await c.post('/api/v1/messages',headers=h,json={'conversation_id':cid2,'content':'2026-10-31'})
  out['short_answer_returns_train_data']='余票' in r.text and '苏州' in r.text and 'error' not in [e['role'] for e in frames(r)]
  # SSE在断连后取消任务并释放会话写锁。
  t=time.perf_counter()
  async with c.stream('POST','/api/v1/messages',headers=h,json={'conversation_id':cid2,'content':'你好，介绍一下你的旅行规划能力'}) as resp:
   async for line in resp.aiter_lines():
    if line.startswith('data: '):break
  async with asyncio.timeout(30):
   r=await c.post('/api/v1/messages',headers=h,json={'conversation_id':cid2,'content':'今天是几号？'})
  out['disconnect_releases_lock']=any(e['role']=='done' and e['code']==200 for e in frames(r));out['disconnect_followup_seconds']=round(time.perf_counter()-t,2)
  cities=(await c.get('/api/v1/cities')).json();out['city_picker_count']=cities['total']
  Path('reports/full_resilience.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
  print({k:v for k,v in out.items() if not k.endswith('events') and not k.endswith('reply')})
if __name__=='__main__':asyncio.run(main())
