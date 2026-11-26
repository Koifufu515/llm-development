"""重启前后比较真实PG checkpoint、长期Store及历史Plan内容，数据只取本地合成验收账号。"""
import asyncio,json,hashlib,sys
from pathlib import Path
from sqlalchemy import select
from langgraph.graph import StateGraph,START,END
from app.config import Settings
from app.full.database import Database,Conversation,Plan,public
from app.full.agent import FullState
from app.full.workflow import Services
from app.core.checkpointer import open_checkpointer
from app.core.store import open_store
async def main():
 mode=sys.argv[1];path=Path('reports/reference-restart-before.json');previous=json.loads(path.read_text()) if mode!='record' else None
 db=Database(Settings())
 async with open_checkpointer(Settings()) as cp,open_store(Settings()) as store:
  b=StateGraph(FullState);b.add_node('read_only',lambda s:{});b.add_edge(START,'read_only');b.add_edge('read_only',END);s=Services.__new__(Services);s.reader=b.compile(checkpointer=cp);s.store=store
  try:
   async with db.session() as session:
    conv=await session.get(Conversation,previous['conversation_id']) if previous else await session.scalar(select(Conversation).where(Conversation.title=='预算多版本验收').order_by(Conversation.created_at.desc()))
    plans=(await session.scalars(select(Plan).where(Plan.conversation_id==conv.id).order_by(Plan.revision))).all()
    artifacts=[{k:v for k,v in public(p).items() if k not in ('updated_at','created_at')} for p in plans]
   state={k:v for k,v in (await s.state(conv.id)).items() if k!='messages'};memory=await s.memory(conv.user_id)
   digest=lambda value:hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,default=str).encode()).hexdigest()
   snapshot={'conversation_id':conv.id,'checkpoint_sha256':digest(state),'memory_sha256':digest(memory),'plans_sha256':digest(artifacts),'plan_versions':len(plans)}
   if mode=='record':path.write_text(json.dumps(snapshot,indent=2));print('recorded',snapshot)
   else:
    result={'scope':__doc__,'before':previous,'after':snapshot,'passed':previous==snapshot};Path('reports/reference-restart.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('restart_persistence',result['passed'])
  finally:await db.close()
asyncio.run(main())
