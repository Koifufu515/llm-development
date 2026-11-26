"""按原文3.6恢复快照：先验SHA，沿用chunk_id，只为子块重新计算真实向量。

默认恢复为building版本，绝不自动替换active集合。显式蓝绿切换需调用者另做验收。
"""
import asyncio,argparse,gzip,hashlib,json,sys
from pathlib import Path
from uuid import uuid4,UUID
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.infra.db import init_pool,close_pool,acquire
from quarry.infra.embed import get_embedder
from quarry.infra.settings import get_settings
from quarry.ingest.indexer import _UPSERT_SQL,_tsvector_input
from quarry.common.vectors import to_halfvec_literal
async def restore(path:Path,tenant_slug:str):
 manifest=json.loads((path/'manifest.json').read_text())
 for name,sha in manifest.items():
  if name not in {'collection.json','documents.jsonl.gz','chunks.jsonl.gz'}:raise ValueError('非法清单路径')
  if hashlib.sha256((path/name).read_bytes()).hexdigest()!=sha:raise ValueError('快照校验失败：'+name)
 coll=json.loads((path/'collection.json').read_text());s=get_settings()
 if coll['embed_model']!=s.model_embed or coll['embed_dim']!=s.embed_dim:raise ValueError('快照模型/维度与当前模型不同；先配置匹配模型再恢复')
 def read(name):
  with gzip.open(path/name,'rt',encoding='utf-8')as f:return [json.loads(line)for line in f if line.strip()]
 docs=read('documents.jsonl.gz');chunks=read('chunks.jsonl.gz');children=[r for r in chunks if r['level']==1]
 # 失败重试先检查已完整提交的building版本，不先重复烧向量化费用。
 async with acquire()as c:
  existing=await c.fetchval("SELECT k.id FROM collections k JOIN tenants t ON t.id=k.tenant_id WHERE t.slug=$1 AND k.slug=$2 AND k.status='building' AND k.embed_model=$3 AND k.embed_dim=$4",tenant_slug,coll['slug'],coll['embed_model'],coll['embed_dim'])
  if existing:
   rows=await c.fetch('SELECT chunk_id,content,level,embedding IS NOT NULL has_vector FROM chunks WHERE collection_id=$1',existing)
   if {(r['chunk_id'],r['content'],r['level'])for r in rows}=={(r['chunk_id'],r['content'],r['level'])for r in chunks} and all(r['has_vector']for r in rows if r['level']==1):
    return {'collection_id':str(existing),'status':'building','documents':len(docs),'chunks':len(chunks),'reembedded_children':0,'chunk_ids_preserved':True,'already_restored':True}
   raise ValueError('此租户已有不同或未完成的building版本；保留该版本，请指定另一个--tenant')
 texts=[(' > '.join(c['heading_path'])+'\n'if c['heading_path']else'')+c['content']for c in children]
 vectors=await get_embedder().embed(texts);vecs={c['chunk_id']:v for c,v in zip(children,vectors)}
 async with acquire()as c,c.transaction():
  tenant=await c.fetchval('INSERT INTO tenants(slug,name)VALUES($1,$1)ON CONFLICT(slug)DO UPDATE SET name=EXCLUDED.name RETURNING id',tenant_slug)
  cid=await c.fetchval("INSERT INTO collections(tenant_id,slug,name,embed_model,embed_dim,chunk_policy,status)VALUES($1,$2,$2,$3,$4,$5,'building')RETURNING id",tenant,coll['slug'],coll['embed_model'],coll['embed_dim'],coll['chunk_policy'])
  mapping={}
  for d in docs:
   uid=uuid4();mapping[d['id']]=uid
   await c.execute("INSERT INTO documents(id,collection_id,source_uri,title,sha256,version,acl_labels,meta,status,parser_tier,indexed_at)VALUES($1,$2,$3,$4,$5,$6,$7,$8,'ready',$9,now())",uid,cid,d['source_uri'],d['title'],d['sha256'],d['version'],d['acl_labels'],d['meta'],'B'if d['source_uri'].endswith('.docx')else'A')
  versions={d['id']:d['version']for d in docs}
  for r in chunks:
   v=vecs.get(r['chunk_id'])
   await c.execute(_UPSERT_SQL,r['chunk_id'],mapping[r['document_id']],cid,versions[r['document_id']],r['level'],r['parent_id'],r['ord'],r['heading_path'],r['content'],r['char_start'],r['char_end'],_tsvector_input(r['content'])if r['level']==1 else None,to_halfvec_literal(v)if v else None,r['acl_labels'],r['meta'])
 return {'collection_id':str(cid),'status':'building','documents':len(docs),'chunks':len(chunks),'reembedded_children':len(vectors),'chunk_ids_preserved':True}
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('path',type=Path);ap.add_argument('--tenant',default='snapshot-recovery');args=ap.parse_args();await init_pool()
 try:out=await restore(args.path,args.tenant)
 finally:await close_pool()
 Path('reports/snapshot-restore.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
