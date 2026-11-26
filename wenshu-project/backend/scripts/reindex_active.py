"""恢复事实快照后重建当前模型的active向量，先确认出站权限和脱敏配置。"""
import asyncio,json
from app.config import Settings
from app.deps import build_container
async def main():
 c=build_container(Settings());await c.mongo.connect();n=0
 try:
  for doc in await c.store.list_documents(status='active'):await c.indexer.reindex(doc['_id']);n+=1
  print(json.dumps({'active_documents_reindexed':n,'model':c.settings.embedding_model,'dimension':c.settings.embedding_dim}))
 finally:
  await c.mongo.close();await c.vector_store.close();await c.llm.close();await c.relay.close()
if __name__=='__main__':asyncio.run(main())
