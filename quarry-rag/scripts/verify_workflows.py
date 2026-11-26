"""隔离集合的真实PG/Redis/向量接口工作流验收；不修改已有攻略。"""
import asyncio,json,sys
from pathlib import Path
from uuid import uuid4
from datetime import date,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.scripts.ingest_corpus import ingest_file
from quarry.ingest.splitter import DEFAULT_POLICY
from quarry.ingest.collections import blue_green_switch
from quarry.facts.attach import fetch_mentions,FactMasker
from quarry.facts.official import replace_facts,coverage
from quarry.facts.contract import norm_entity

async def main():
 await init_pool();tenant=None;out={};folder=Path('corpus')/('workflow-'+uuid4().hex[:8]);folder.mkdir();path=folder/'policy.md'
 try:
  async with acquire() as c:
   tenant=await c.fetchval("INSERT INTO tenants(slug,name)VALUES($1,'隔离验收')RETURNING id",folder.name)
   coll=await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim,chunk_policy)VALUES($1,$2,'隔离验收','text-embedding-v4',1024,$3)RETURNING id",tenant,folder.name,DEFAULT_POLICY)
  first='# 验收制度\n\n## 餐补\n每天餐补100元。\n\n## 交通\n交通报销只允许经济舱。\n\n## 住宿\n住宿每日不超过300元。\n'
  async def ingest(text):
   path.write_text(text);return await ingest_file(path,coll,folder.name,['public'],{},DEFAULT_POLICY)
  out['initial']=await ingest(first);out['repeat']=await ingest(first)
  second=first.replace('100元','120元');out['one_change']=await ingest(second)
  third=second.replace('## 交通\n交通报销只允许经济舱。\n\n','');out['delete_section']=await ingest(third)
  assert out['initial']['vectorized']==3 and out['repeat']['skipped']
  assert out['one_change']['vectorized']==1 and out['one_change']['reused']==2
  assert out['delete_section']['vectorized']==0
  async with acquire()as c:
   out['versions']=[dict(r)for r in await c.fetch('SELECT version,status FROM documents WHERE collection_id=$1 ORDER BY version',coll)]
   assert [r['status']for r in out['versions']]==['superseded','superseded','ready']
   assert await c.fetchval("SELECT count(*) FROM chunks WHERE collection_id=$1 AND content LIKE '%经济舱%'",coll)==0
   # 权限刷新必须同时更新文档与父子块。
   async with c.transaction():
    await c.execute("UPDATE documents SET acl_labels=ARRAY['org:test'] WHERE collection_id=$1",coll)
    await c.execute("UPDATE chunks SET acl_labels=ARRAY['org:test'] WHERE collection_id=$1",coll)
   assert await c.fetchval("SELECT count(*) FROM chunks WHERE collection_id=$1 AND acl_labels&&ARRAY['public']",coll)==0
   green=await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim,status)VALUES($1,$2,'绿','text-embedding-v4',1024,'building')RETURNING id",tenant,folder.name)
  await blue_green_switch(coll,green)
  async with acquire()as c:assert await c.fetchval("SELECT id FROM collections WHERE tenant_id=$1 AND slug=$2 AND status='active'",tenant,folder.name)==green
  await blue_green_switch(green,coll);out['blue_green_switch_and_rollback']=True
  # 演示专用值，不是现实票价。覆盖官方值替换、过期、未核实与旧值遮蔽。
  async with acquire()as c:
   parent=await c.fetchrow("SELECT chunk_id,content FROM chunks WHERE collection_id=$1 AND level=0 ORDER BY ord LIMIT 1",coll)
   text=parent['content'];quote='120元';start=text.index(quote)
   await c.execute("INSERT INTO fact_mentions(collection_id,chunk_id,entity_name,entity_norm,attribute,qualifier,value,quote,span_start,span_end)VALUES($1,$2,'演示景点',$3,'ticket_price','全年','120',$4,$5,$6)",coll,parent['chunk_id'],norm_entity('演示景点'),quote,start,start+len(quote))
   record=dict(entity='演示景点',match_keys=[norm_entity('演示景点')],attribute='ticket_price',qualifier='全年',value='150',verified_at=date.today(),source_url='https://example.com/demo-only')
   await replace_facts(c,coll,[record]);a=await coverage(c,coll,90);assert a['counts']['verified']==1 and a['conflicts']
   rows=await fetch_mentions(c,coll,[parent['chunk_id']],['org:test']);masker=FactMasker(rows,90);masked=masker.mask(parent['chunk_id'],text);contexts,facts=masker.finalize([masked]);assert '120'not in contexts[0]and facts[0][0].value=='150'
   record['verified_at']=date.today()-timedelta(days=91);await replace_facts(c,coll,[record]);assert (await coverage(c,coll,90))['counts']['expired']==1
   await replace_facts(c,coll,[]);assert (await coverage(c,coll,90))['counts']['unverified']==1
   assert not await fetch_mentions(c,coll,[parent['chunk_id']],['public'])
   out['fact_verified_expired_unverified_conflict_mask_acl']=True
   async with c.transaction():
    await c.execute("UPDATE documents SET status='retired' WHERE collection_id=$1",coll)
    await c.execute('DELETE FROM chunks WHERE collection_id=$1',coll)
   assert await c.fetchval('SELECT count(*)FROM fact_mentions WHERE collection_id=$1',coll)==0
   out['withdrawal_and_fact_cascade']=True
 finally:
  if tenant:
   async with acquire()as c:await c.execute('DELETE FROM tenants WHERE id=$1',tenant)
  await close_pool();path.unlink(missing_ok=True);folder.rmdir()
 Path('reports/workflows.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
