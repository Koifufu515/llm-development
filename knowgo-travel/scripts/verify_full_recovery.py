from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
TODAY=datetime.now(ZoneInfo("Asia/Shanghai")).date()
import asyncio,json,secrets
from datetime import timedelta
from pathlib import Path
from app.main import app
from app.full.database import User,Conversation,Card,now
from app.full.domain import Requirement
async def main():
 async with app.router.lifespan_context(app):
  s=app.state.full;out={};req=Requirement(departure_city='上海',destinations=['苏州'],departure_date=(TODAY+timedelta(days=1)).isoformat(),travel_days=1)
  async with s.db.session() as db:
   u=User(email='recovery-'+secrets.token_hex(5)+'@kg.local',password_hash='disabled-test-user');db.add(u);await db.flush();conv=Conversation(user_id=u.id,title='注入故障恢复测试');db.add(conv);await db.flush()
   candidate={'segment_id':'s1','option_id':'controlled-fixture','name':'受控测试候选，不是真实班次','availability':'有','price_yuan':10,'mode':'train','from':'上海','to':'苏州','date':(TODAY+timedelta(days=1)).isoformat()}
   card=Card(conversation_id=conv.id,skill_name='train_multi_segment',revision=1,payload={'mode':'train','segments':[{'segment_id':'s1','options':[candidate]}]},expires_at=now()+timedelta(minutes=10));db.add(card);await db.commit();cid=conv.id;uid=u.id;cardid=card.id
  await s.write(cid,{'requirement':req.model_dump(mode='json'),'user_id':uid,'current_step':'transport_planning','revision':1,'active_card':{'id':cardid,'skill_name':'train_multi_segment'}})
  selections=[{'segment_id':'s1','option_id':'controlled-fixture'}];realwrite=s.write
  async def fail_once(*args,**kwargs):raise RuntimeError('injected checkpoint failure')
  async def emit(*args,**kwargs):pass
  s.write=fail_once
  try:await s.submit(cid,uid,cardid,1,selections,emit)
  except RuntimeError:out['injected_failure_observed']=True
  finally:s.write=realwrite
  async with s.db.session() as db:out['receipt_committed_before_checkpoint']=(await db.get(Card,cardid)).submitted is not None
  # 阻止此控制夹具进入真实行程生成；仅核对续跑取得已持久选择。
  realadvance=s.advance
  async def stop_after_recovery(*args,**kwargs):return {'text':'recovery inspected','extra':{}}
  s.advance=stop_after_recovery
  try:await s.submit(cid,uid,cardid,1,selections,emit)
  finally:s.advance=realadvance
  state=await s.state(cid);out['retry_restores_checkpoint']=state['current_step']=='accommodation_planning' and state['selected_transport'][0]['option_id']=='controlled-fixture'
  async with s.db.session() as db:row=await db.get(Conversation,cid);row.deleted_at=now();await db.commit()
  out['scope']='真实PostgreSQL+Checkpoint故障注入；候选为明确标记的测试夹具，不是真实交通查询，测试会话已软删。'
  Path('reports/full_card_recovery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
if __name__=='__main__':asyncio.run(main())
