"""当版完整分步状态机与快速通道：同出行需求，脚本立即选卡，不计人为思考。
同一自动规则挑选真实候选；每次清本版本苏州查询缓存，保存全部请求/错误/调用数。
"""
import asyncio,json,secrets,time,os
from pathlib import Path
import httpx
from redis.asyncio import Redis
from app.full.capabilities import auto_pick
ROOT=Path(os.getenv('FLOW_REPORT','reports/reference-flow-benchmark.json'))
async def main():
 rows=[];cache=Redis.from_url('redis://127.0.0.1:56379/0',decode_responses=True)
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8001',trust_env=False,timeout=420) as c:
  user=(await c.post('/api/v1/users/register',json={'username':'bench-'+secrets.token_hex(5),'email':'bench-'+secrets.token_hex(5)+'@kg.local','password':'KnowgoReviewDemo2026!'})).json();h={'Authorization':'Bearer '+user['access_token']}
  async def clean():
   async for key in cache.scan_iter('kg:rag:*'):
    try:
     value=json.loads(await cache.get(key));results=value.get('results',[])
     if value.get('pipeline','').startswith('reference-0099-v3') and results and results[0].get('city')=='苏州':await cache.delete(key)
    except (ValueError,TypeError):pass
  async def sse(path,body,cid):
   events=[];start=time.perf_counter()
   async with c.stream('POST',path,headers=h,json=body) as response:
    response.raise_for_status()
    async for line in response.aiter_lines():
     if line.startswith('data: '):events.append({'seconds':time.perf_counter()-start,**json.loads(line[6:])})
   messages=(await c.get('/api/v1/messages',headers=h,params={'conversation_id':cid})).json()['items']
   result={'elapsed':time.perf_counter()-start,'events':events,'metrics':messages[-1].get('extra',{}).get('metrics',{})}
   if not events or events[-1].get('code')!=200:raise ValueError('SSE未正常结束：'+str(events[-2:]))
   text=''
   for event in events:
    if event['role']=='assistant_reset':text=''
    elif event['role']=='assistant':text+=event['content'] or ''
   result['display_matches_saved']=text==messages[-1]['extra'].get('original')
   return result
  for repeat in range(1,int(os.getenv('FLOW_ROUNDS','3'))+1):
   for mode in (('standard','express') if repeat%2 else ('express','standard')):
    await clean();cid=(await c.post('/api/v1/conversations',headers=h,json={'title':f'基准{repeat}-{mode}'})).json()['id']
    req={'departure_city':'上海','destinations':['苏州'],'departure_date':'2026-11-01','travel_days':3,'adult_count':1,'children_count':0,'budget_max':5000,'transport_types':['train'],'auto_confirm':mode=='express'}
    trial={'repeat':repeat,'mode':mode,'conversation_id':cid,'requirement':req,'turns':[]};rows.append(trial);started=time.perf_counter()
    try:
     trial['turns'].append(await sse(f'/api/v1/conversations/{cid}/requirement',req,cid))
     for step in range(7):
      state=(await c.get('/api/v1/conversations/'+cid,headers=h)).json()['state']
      if state.get('current_step')=='budget_summarization':break
      if state.get('current_step')=='destination_recommendation':
       trial['turns'].append(await sse('/api/v1/messages',{'conversation_id':cid,'content':'确认'},cid));continue
      active=state.get('active_card')
      if not active:raise ValueError('缺少预期卡片，step='+str(state.get('current_step')))
      card=(await c.get('/api/v1/cards/'+active['id'],headers=h)).json()
      trial['turns'].append(await sse('/api/v1/skills/'+card['skill_name']+'/submit',{'conversation_id':cid,'card_id':card['id'],'revision':card['revision'],'selections':auto_pick(card['data'])},cid))
     plan=(await c.get('/api/v1/plans/'+state['plan_id'],headers=h)).json()
     trial.update({'status':'ok','seconds':time.perf_counter()-started,'plan_id':plan['id'],'days':len(plan['body']['days']),'legacy_days':len(plan['plan_data']['itinerary_list']),'llm_calls':sum(t['metrics'].get('llm_calls',0) for t in trial['turns']),'llm_errors':sum(t['metrics'].get('llm_errors',0) for t in trial['turns']),'display_matches_saved':all(t['display_matches_saved'] for t in trial['turns'])})
    except Exception as exc:trial.update({'status':'error','error':type(exc).__name__,'message':str(exc)[:700],'seconds':time.perf_counter()-started})
    ROOT.write_text(json.dumps({'scope':__doc__,'synthetic_account':user['user']['username'],'model_policy':'Qwen Plus主模型与RAG辅助，Turbo429已另存；各3轮交替，当前网络与供应商仍有抖动。','rows':rows},ensure_ascii=False,indent=2));print(repeat,mode,{k:v for k,v in trial.items() if k in ('status','seconds','llm_calls','llm_errors','display_matches_saved','message')},flush=True)
 await cache.aclose()
asyncio.run(main())
