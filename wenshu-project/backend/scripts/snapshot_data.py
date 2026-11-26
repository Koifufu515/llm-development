"""仅备份业务事实与词表；不导出账号、会话、密钥。恢复默认要求空目标库。"""
import argparse,asyncio,json
from pathlib import Path
from bson import json_util
from app.config import Settings
from app.deps import build_container
COLLECTIONS=['departments','documents','chunks','doc_relations','glossary']
async def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['export','restore']);p.add_argument('file');p.add_argument('--redact',action='store_true');a=p.parse_args();c=build_container(Settings());await c.mongo.connect()
 try:
  if a.mode=='export':
   data={name:await c.store.find(name)for name in COLLECTIONS};text=json_util.dumps(data,ensure_ascii=False)
   if a.redact:
    from app.llm.privacy import redact
    text=redact(text)
   target=Path(a.file);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text);target.chmod(0o600)
  else:
   data=json_util.loads(Path(a.file).read_text())
   if set(data)-set(COLLECTIONS):raise ValueError('快照包含未允许集合')
   if any([await c.store.count(name)for name in COLLECTIONS]):raise ValueError('恢复仅允许空目标业务库，禁止覆盖现有数据')
   for name,rows in data.items():
    for row in rows:await c.store.upsert(name,row)
  print(json.dumps({'mode':a.mode,'counts':{name:len(rows)for name,rows in data.items()},'vectors':'未包含；恢复后执行reindex，必须保持原模型和维度'},ensure_ascii=False))
 finally:await c.mongo.close()
if __name__=='__main__':asyncio.run(main())
