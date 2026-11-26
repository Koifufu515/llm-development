"""真实库EXPLAIN，对照共享CTE物化与直接索引扫描。"""
import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.infra.embed import get_embedder
from quarry.common.vectors import to_halfvec_literal
from quarry.retrieval.query import build_tsquery
from quarry.retrieval.pg.searcher import _HYBRID_SQL
async def main():
 await init_pool()
 try:
  vec=to_halfvec_literal((await get_embedder().embed(['兵马俑的门票多少钱']))[0]);tsq=build_tsquery('兵马俑的门票多少钱');out={}
  async with acquire()as c:
   coll=await c.fetchval("SELECT id FROM collections WHERE slug='travel-guide' AND status='active'")
   out['indexes']=[dict(r)for r in await c.fetch("SELECT indexrelname,pg_relation_size(indexrelid) bytes FROM pg_stat_user_indexes WHERE relname='chunks' ORDER BY bytes DESC")]
   for name,sql,args in [
    ('hybrid_natural',_HYBRID_SQL,[coll,['public'],{},vec,tsq,50,50,.5,.5,60,10]),
    ('direct',"SELECT chunk_id FROM chunks WHERE collection_id=$1 AND level=1 AND acl_labels&&ARRAY['public'] ORDER BY embedding<=>$2::halfvec(1024) LIMIT 5",[coll,vec]),
    ('shared_cte',"WITH filtered AS (SELECT * FROM chunks WHERE collection_id=$1 AND level=1) (SELECT chunk_id FROM filtered ORDER BY embedding<=>$2::halfvec(1024) LIMIT 5) UNION ALL (SELECT chunk_id FROM filtered WHERE acl_labels&&ARRAY['public'] LIMIT 5)",[coll,vec])]:
    async with c.transaction():
     if name!='hybrid_natural':
      await c.execute('SET LOCAL enable_seqscan=off');await c.execute('SET LOCAL enable_bitmapscan=off');await c.execute('SET LOCAL enable_sort=off')
     plan=await c.fetch('EXPLAIN (ANALYZE,BUFFERS) '+sql,*args);out[name]='\n'.join(r[0]for r in plan)
   assert 'chunks_embed_hnsw'in out['direct'];assert 'CTE Scan on filtered'in out['shared_cte'] and 'chunks_embed_hnsw'not in out['shared_cte']
   out['fts_and_count']=await c.fetchval("SELECT count(*)FROM chunks WHERE collection_id=$1 AND level=1 AND tokens@@plainto_tsquery('simple',$2)",coll,'兵马俑 的 门票 多少 钱')
   out['fts_or_count']=await c.fetchval("SELECT count(*)FROM chunks WHERE collection_id=$1 AND level=1 AND tokens@@to_tsquery('simple',$2)",coll,tsq)
 finally:await close_pool()
 Path('reports/sql-plans.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('HNSW直接索引、共享CTE物化、OR/AND和索引大小已保存')
if __name__=='__main__':asyncio.run(main())
