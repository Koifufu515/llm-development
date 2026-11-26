"""本机真实HTTP/SDK/上传验收，密钥不输出。"""
import asyncio,httpx,re,json,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sdk'))
from quarry_client import QuarryClient,render_for_prompt
async def main():
 base=os.getenv('QUARRY_URL','http://127.0.0.1:8110');key=re.search(r'qr_[\w-]+',Path('private/knowgo-key.txt').read_text()).group();auth={'Authorization':f'Bearer {key}'};checks={}
 async with httpx.AsyncClient(base_url=base,timeout=30)as c:
  for _ in range(40):
   try:
    probe=await c.get('/healthz')
    if probe.status_code==200 and probe.headers.get('content-type','').startswith('application/json'):break
   except httpx.TransportError:pass
   await asyncio.sleep(.25)
  else:raise RuntimeError('接口未就绪')
  for name,path,method,payload,headers,expect in [('health','/healthz','GET',None,{},200),('no_key','/v1/search','POST',{'collection':'travel-guide','query':'苏州'},{},401),('collections','/v1/collections','GET',None,auth,200),('forbidden','/v1/search','POST',{'collection':'corp-policy','query':'餐补','caller_labels':['org:demo-corp']},auth,403),('invalid','/v1/search','POST',{'collection':'travel-guide','query':'苏州','top_k':99},auth,422),('search','/v1/search','POST',{'collection':'travel-guide','query':'南普陀寺开放时间','top_k':5},auth,200)]:
   r=await c.request(method,path,json=payload,headers=headers);checks[name]={'status':r.status_code,'body':r.json()};assert r.status_code==expect,(name,r.status_code)
  upload_key=re.search(r'qr_[\w-]+',Path('private/ingest-key.txt').read_text()).group();write_auth={'Authorization':f'Bearer {upload_key}'}
  blocked=await c.post('/v1/documents',params={'collection_slug':'travel-guide'},files={'file':('blocked.md',b'not allowed')},headers=auth);assert blocked.status_code==403
  r=await c.post('/v1/documents',params={'collection_slug':'travel-guide'},files={'file':('upload-smoke.md','# 上传验收\n\n## 信息\nQuarry接入队列验收，文档将在后台处理。\n'.encode())},headers=write_auth);assert r.status_code==200;doc=r.json()['document_id'];state={}
  for _ in range(20):
   r=await c.get('/v1/documents/'+doc,headers=auth);state=r.json()
   if state.get('status')in ['ready','failed']:break
   await asyncio.sleep(1)
  assert state.get('status')=='ready',state
  checks['upload']={'document_id':doc,'state':state}
 async with QuarryClient(base,key)as c:
  result=await c.search('travel-guide','南普陀寺开放时间',top_k=5);assert result.evidences;prompt=render_for_prompt(result);assert 'F1'in prompt;checks['sdk']={'evidences':len(result.evidences),'prompt_chars':len(prompt)}
 Path('reports/api-live-second.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print({k:v.get('status',v.get('state',v))for k,v in checks.items()})
if __name__=='__main__':asyncio.run(main())
