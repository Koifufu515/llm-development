"""重新验证已缓存的模型建议，保留旧快照；不重复调用模型。"""
import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.facts.extract import Stats,to_mentions,save
async def main():
 await init_pool();stats=Stats();before=[];after=0
 try:
  async with acquire()as c:
   rows=await c.fetch("SELECT m.*,c.content FROM fact_mentions m JOIN chunks c ON c.collection_id=m.collection_id AND c.chunk_id=m.chunk_id JOIN collections k ON k.id=m.collection_id WHERE k.slug='travel-guide' AND k.status='active' ORDER BY m.chunk_id,m.span_start")
  groups={}
  for r in rows:
   before.append(dict(r));groups.setdefault((r['collection_id'],r['chunk_id']),[]).append(r)
  Path('reports/fact-mentions-before-revalidation.json').write_text(json.dumps(before,ensure_ascii=False,default=str,indent=2))
  for (cid,chunk),rs in groups.items():
   items=[dict(entity=r['entity_name'],attribute=r['attribute'],qualifier=r['qualifier'],value=r['value'],quote=r['quote'])for r in rs]
   got=to_mentions(items,rs[0]['content'],stats);await save(cid,chunk,'qwen-flash+entity-validation',got);after+=len(got)
 finally:await close_pool()
 out={'before':len(before),'after':after,'dropped':stats.dropped,'model_calls':0};Path('reports/fact-revalidation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
