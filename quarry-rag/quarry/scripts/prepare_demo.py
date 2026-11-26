"""新环境复现原文3/6章：幂等接入，给demo旅行集合启用事实层并离线抽取。"""
import asyncio
from pathlib import Path
from quarry.facts.official import load_csv,replace_facts
from dataclasses import asdict
from quarry.scripts.ingest_corpus import main as ingest
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.infra.settings import get_settings
from quarry.facts.extract import extract_collection
async def main():
 await ingest()
 await init_pool()
 try:
  async with acquire()as c:
   cid=await c.fetchval("UPDATE collections k SET facts_enabled=true FROM tenants t WHERE k.tenant_id=t.id AND t.slug='demo' AND k.slug='travel-guide' AND k.status='active' RETURNING k.id")
  if cid:
   print('离线事实抽取：',asdict(await extract_collection(get_settings(),cid)))
   # 只在空表初次导入随包的官方维护数据，重跑不覆盖使用者已维护的值。
   path=Path('official/travel-guide.csv')
   if path.exists():
    rows,errors=load_csv(path)
    if errors:raise ValueError('官方CSV不合法：'+str(errors))
    async with acquire()as c:
     if rows and not await c.fetchval('SELECT count(*)FROM facts WHERE collection_id=$1',cid):
      await replace_facts(c,cid,rows)
      print('初始化官方维护值：',len(rows))
 finally:await close_pool()
if __name__=='__main__':asyncio.run(main())
