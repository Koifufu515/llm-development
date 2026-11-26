"""真实HTTP：两个租户同名集合、同chunk_id、同public标签仍严格隔离。"""
import asyncio,json,secrets,sys,subprocess
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.infra.embed import get_embedder
from quarry.api.security import hash_key
from quarry.ingest.indexer import _UPSERT_SQL,_tsvector_input
from quarry.common.vectors import to_halfvec_literal
async def main():
 await init_pool();tenants=[];keys=[];out=[]
 try:
  texts=['租户A专属内容：测试园区开放时间09:00-17:00。','租户B专属内容：测试园区开放时间10:00-18:00。'];vectors=await get_embedder().embed(texts)
  async with acquire()as c:
   for i in range(2):
    tid=await c.fetchval("INSERT INTO tenants(slug,name)VALUES($1,$2)RETURNING id",'api-scope-'+uuid4().hex,'tenant-'+str(i));tenants.append(tid)
    cid=await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim)VALUES($1,'tenant-check',$2,'text-embedding-v4',1024)RETURNING id",tid,'tenant-'+str(i))
    doc=await c.fetchval("INSERT INTO documents(collection_id,source_uri,sha256,title,status,parser_tier,acl_labels)VALUES($1,'shared/x.md','fixture',$2,'ready','A','{public}')RETURNING id",cid,'tenant-'+str(i))
    for level,chunk in [(0,'same-parent'),(1,'same-child')]:
     await c.execute(_UPSERT_SQL,chunk,doc,cid,1,level,None if level==0 else 'same-parent',0,[],texts[i],0,len(texts[i]),_tsvector_input(texts[i])if level else None,to_halfvec_literal(vectors[i])if level else None,['public'],{})
    raw='qr_'+secrets.token_urlsafe(32);kid=uuid4().hex[:8];keys.append((kid,raw))
    await c.execute("INSERT INTO api_keys(key_id,key_hash,caller_id,labels,collections,rate_limit,tenant_id)VALUES($1,$2,'tenant-check','{public,role:ingest}','{tenant-check}',120,$3)",kid,hash_key(raw),tid)
  async with httpx.AsyncClient(base_url='http://127.0.0.1:8113',timeout=20)as c:
   docs=[]
   for i,(_,raw)in enumerate(keys):
    auth={'Authorization':f'Bearer {raw}'}
    r=await c.get('/v1/collections',headers=auth);assert r.status_code==200 and r.json()['collections']==[{'slug':'tenant-check','title':'tenant-'+str(i),'facts_enabled':False}]
    r=await c.post('/v1/search',headers=auth,json={'collection':'tenant-check','query':'测试园区几点开放','use_rerank':False,'use_facts':False,'tenant_id':str(tenants[1-i]),'caller_labels':['public']});assert r.status_code==200
    es=r.json()['evidences'];assert es and all(e['citation']['title']=='tenant-'+str(i)for e in es);out.append({'tenant':i,'matching_evidence_title':es[0]['citation']['title'],'same_chunk_id':es[0]['chunk_id']})
    r=await c.post('/v1/documents',params={'collection_slug':'tenant-check'},headers=auth,files={'file':('same.md',f'# 租户上传\n\n## 内容\n这是租户{i}的独立文件。'.encode())});assert r.status_code==200;did=r.json()['document_id'];docs.append(did)
    for _ in range(25):
     state=(await c.get('/v1/documents/'+did,headers=auth)).json()
     if state.get('status')in['ready','failed']:break
     await asyncio.sleep(.4)
    assert state.get('status')=='ready',state
   for i,(_,raw)in enumerate(keys):assert (await c.get('/v1/documents/'+docs[1-i],headers={'Authorization':f'Bearer {raw}'})).status_code==404
  async with acquire()as c:
   uris=await c.fetch('SELECT source_uri FROM documents WHERE collection_id IN(SELECT id FROM collections WHERE tenant_id=ANY($1::uuid[])) AND source_uri LIKE $2',tenants,'_tenants/%');assert len(uris)==2 and len({r['source_uri']for r in uris})==2
  result={'same_slug_same_labels_same_ids_isolated':out,'tenant_upload_paths_distinct':True,'foreign_document_status':404}
  Path('reports/tenant-api.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result)
 finally:
  async with acquire()as c:
   await c.execute('DELETE FROM api_keys WHERE key_id=ANY($1::text[])',[k for k,_ in keys]);await c.execute('DELETE FROM tenants WHERE id=ANY($1::uuid[])',tenants)
  await close_pool()
  if tenants:
   # 仅清理本实验生成的UUID子目录，不碰其他语料。
   code='import json,sys,shutil;from pathlib import Path;[shutil.rmtree(Path("/app/corpus/_tenants")/x,ignore_errors=True)for x in json.load(sys.stdin)]'
   p=subprocess.run(['docker','--context','colima-knowgo','compose','-p','quarry-rag','exec','-T','worker','python','-c',code],input=json.dumps([str(t)for t in tenants]),text=True,capture_output=True);assert p.returncode==0
if __name__=='__main__':asyncio.run(main())
