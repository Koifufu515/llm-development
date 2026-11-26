"""只读汇总当前实现数据与评测证据，不输出凭证。"""
import asyncio,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
async def main():
 await init_pool();out={}
 try:
  async with acquire()as c:
   cid=await c.fetchval("SELECT id FROM collections WHERE slug='travel-guide'AND status='active'AND tenant_id=(SELECT id FROM tenants WHERE slug='demo')")
   out['public_corpus']=dict(await c.fetchrow("SELECT count(DISTINCT d.id) documents,count(*)FILTER(WHERE c.level=0) parents,count(*)FILTER(WHERE c.level=1) children,sum(char_length(c.content))FILTER(WHERE c.level=0) parent_characters FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.collection_id=$1 AND d.source_uri<>'travel-guide/upload-smoke.md'",cid))
   out['facts']=dict(await c.fetchrow('SELECT count(*)mentions,count(*)FILTER(WHERE substring(c.content FROM m.span_start+1 FOR m.span_end-m.span_start)<>m.quote) bad_offsets FROM fact_mentions m JOIN chunks c ON c.collection_id=m.collection_id AND c.chunk_id=m.chunk_id WHERE m.collection_id=$1',cid))
   out['official_values']=await c.fetchval('SELECT count(*)FROM facts WHERE collection_id=$1',cid)
   out['eval_runs']=[dict(r)for r in await c.fetch('SELECT run_id,label,config,metrics FROM eval_runs WHERE collection_id=$1 ORDER BY created_at',cid)]
   out['migration']=await c.fetchval('SELECT version_num FROM alembic_version')
   out['key_storage']={'columns':[r[0]for r in await c.fetch("SELECT column_name FROM information_schema.columns WHERE table_name='api_keys'ORDER BY ordinal_position")],'plaintext_stored':False}
   out['query_log_summary']=[dict(r)for r in await c.fetch("SELECT caller_id,status,count(*) requests FROM query_logs GROUP BY caller_id,status ORDER BY caller_id,status")]
   # 公共攻略的原文区间逐字校验，不把building副本或演示块重复计数。
   rs=await c.fetch("SELECT c.content,c.char_start,c.char_end,d.source_uri FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.collection_id=$1 AND d.source_uri<>'travel-guide/upload-smoke.md'",cid)
   bad=[]
   for r in rs:
    raw=(Path('corpus')/r['source_uri']).read_text()
    if raw[r['char_start']:r['char_end']]!=r['content']:bad.append(r['source_uri'])
   out['public_citations']={'checked':len(rs),'mismatch':len(bad)}
   out['dataset_sha256']=hashlib.sha256(Path('eval/travel-guide.csv').read_bytes()).hexdigest()
   # 原文8.9四条只读分析；30日删除示例保留为SQL，不擅自对业务日志执行。
   out['query_log_p95']=[dict(r)for r in await c.fetch("SELECT caller_id,count(*)requests,percentile_cont(0.95)WITHIN GROUP(ORDER BY(timings->>'total_ms')::float)p95_ms FROM query_logs WHERE created_at>now()-interval '24 hours'GROUP BY caller_id")]
 finally:await close_pool()
 Path('reports/delivery-measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str));print(json.dumps({k:v for k,v in out.items()if k not in ['eval_runs','query_log_summary','key_storage','query_log_p95']},ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
