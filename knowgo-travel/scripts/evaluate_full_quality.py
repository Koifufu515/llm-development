import asyncio,json
from pathlib import Path
from sqlalchemy import select
from app.main import app
from app.full.database import Plan,Conversation,Message
from app.full.domain import Requirement
from app.full.quality import evaluate
async def main():
 out=[];previous=[]
 async with app.router.lifespan_context(app):
  s=app.state.full
  async with s.db.session() as db:plans=(await db.scalars(select(Plan).order_by(Plan.updated_at.desc()).limit(8))).all()
  for p in plans:
   state=await s.state(p.conversation_id)
   if state.get('revision')!=p.revision or not state.get('plan_id'):continue
   async with s.db.session() as db:
    m=await db.scalar(select(Message).where(Message.conversation_id==p.conversation_id,Message.role=='assistant').order_by(Message.created_at.desc()))
   if not m or not m.extra.get('sources'):continue
   req=Requirement.model_validate(state['requirement']);previous.append({'id':p.id,'quality':p.quality})
   result=await evaluate(s.model,{**req.model_dump(mode='json'),'budget':p.budget},p.body,[*state.get('selected_transport',[]),*state.get('selected_hotels',[])],m.extra['sources'])
   out.append({'id':p.id,'title':p.title,'quality':result});Path('reports/full_quality_offline.json').write_text(json.dumps({'scope':'同一GEval规则离线评估真实保存行程；分数是模型裁判评分，不是事实准确率。','results':out},ensure_ascii=False,indent=2));print(p.title,[(r['name'],r['score']) for r in result['metrics']],flush=True)
   if len(out)>=3:break
  Path('reports/full_quality_previous.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
