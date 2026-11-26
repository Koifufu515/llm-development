import asyncio,json
from datetime import datetime,timezone
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi.responses import FileResponse,StreamingResponse
from pydantic import BaseModel,Field,field_validator,model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.config import PROJECT_ROOT
from app.full.database import User,Conversation,Message,Plan,Card,owned,public,now
from app.full.security import current_user,password_hash,verify_password,token_for
from app.full.domain import Requirement,STEPS

router=APIRouter(prefix='/api/v1')

class Credentials(BaseModel):
    email:str|None=Field(default=None,min_length=3,max_length=254,pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    username:str|None=Field(default=None,min_length=1,max_length=50)
    password:str=Field(min_length=8,max_length=256)
    @field_validator('email')
    @classmethod
    def email_lower(cls,v):return v.strip().lower() if v else None
    @model_validator(mode='after')
    def identifier(self):
        if not self.email and not self.username:raise ValueError('请提供用户名或邮箱')
        return self

@router.post('/users/register',status_code=201)
async def register(body:Credentials,request:Request):
    if not body.email:raise HTTPException(422,'注册需要邮箱；登录可使用用户名或邮箱')
    import secrets
    async with request.app.state.full_db.session() as db:
        user=User(email=body.email,username=body.username or body.email.split('@')[0][:30]+'-'+secrets.token_hex(4),password_hash=await password_hash(body.password));db.add(user)
        try:await db.commit()
        except IntegrityError:await db.rollback();raise HTTPException(409,'该用户名或邮箱已注册') from None
        return {'user':public(user),'access_token':token_for(user.id),'token_type':'bearer'}

@router.post('/users/login')
async def login(body:Credentials,request:Request):
    async with request.app.state.full_db.session() as db:
        query=select(User)
        if body.username:query=query.where(User.username==body.username)
        if body.email:query=query.where(User.email==body.email)
        user=await db.scalar(query)
        if user is None or not await verify_password(body.password,user.password_hash):raise HTTPException(401,'邮箱或密码错误')
        return {'user':public(user),'access_token':token_for(user.id),'token_type':'bearer'}

@router.get('/users/me')
async def me(request:Request,user=Depends(current_user)):return {**public(user),'preferences':await request.app.state.full.memory(user.id)}

class ConvCreate(BaseModel):
    title:str=Field(default='新对话',min_length=1,max_length=120)
class ConvPatch(BaseModel):
    title:str|None=Field(default=None,min_length=1,max_length=120)
    status:str|None=Field(default=None,pattern=r'^(active|archived)$')

@router.post('/conversations',status_code=201)
async def create_conv(request:Request,body:ConvCreate=ConvCreate(),user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=Conversation(user_id=user.id,title=body.title);db.add(row);await db.commit()
        await request.app.state.full.write(row.id,{'messages':[],'user_id':user.id,'current_step':'requirement_collection','requirement':{},'revision':0,'itinerary_body':None,'budget':None})
        return public(row)

@router.get('/conversations')
async def conversations(request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        rows=await db.scalars(select(Conversation).where(Conversation.user_id==user.id,Conversation.deleted_at.is_(None)).order_by(Conversation.updated_at.desc()).limit(100))
        return {'items':[public(r) for r in rows]}

@router.get('/conversations/{cid}')
async def conversation(cid:UUID,request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=await owned(db,cid,user.id)
        return {**public(row),'state':{k:v for k,v in (await request.app.state.full.state(str(cid))).items() if k!='messages'}}

@router.patch('/conversations/{cid}')
async def patch_conv(cid:UUID,body:ConvPatch,request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=await owned(db,cid,user.id)
        for k,v in body.model_dump(exclude_none=True).items():setattr(row,k,v)
        await db.commit();return public(row)

@router.delete('/conversations/{cid}')
async def delete_conv(cid:UUID,request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=await owned(db,cid,user.id);row.deleted_at=now();await db.commit();return {'deleted':True}

@router.get('/messages')
async def messages(conversation_id:UUID,request:Request,user=Depends(current_user),limit:int=100):
    async with request.app.state.full_db.session() as db:
        await owned(db,conversation_id,user.id)
        rows=(await db.scalars(select(Message).where(Message.conversation_id==str(conversation_id)).order_by(Message.created_at.desc()).limit(max(1,min(limit,200))))).all()
        return {'items':[public(row) for row in reversed(rows)]}

async def authorize(request,cid,user):
    async with request.app.state.full_db.session() as db:await owned(db,cid,user.id)

def stream_turn(request,cid,user,action):
    services=request.app.state.full
    async def events():
        from app.full.events import EventStream,make_event
        stream=EventStream()
        async def emit(role,content,code=None):await stream.apush(make_event(role,content,code))
        async def worker():
            from app.core.telemetry import RequestMetrics
            from langchain_core.runnables.config import var_child_runnable_config
            metrics=RequestMetrics();status='running'
            context_token=var_child_runnable_config.set({'callbacks':[metrics],'tags':['knowgo-full']})
            try:
                async with services.db.lock(str(cid)):
                    await authorize(request,cid,user)
                    async with asyncio.timeout(420): result=await action(emit)
                    text=result.get('text','');extra=result.get('extra',{})
                    if text and not result.get('streamed'):await emit('assistant',text)
                    # 保留原文与结构化卡片；长文摘要只影响content，不影响重放。
                    saved=text
                    if len(text)>2000:
                        try:
                            response=await services.model.ainvoke('将下列行程摘要为300字以内，保留城市、天数和选择结果，不添加事实：\n'+text)
                            saved=str(response.content)
                        except Exception:saved=text
                    extra['metrics']=metrics.snapshot()
                    await services.save_message(str(cid),'assistant',saved,{'original':text,**extra})
                    async with services.db.session() as db:
                        conv=await owned(db,cid,user.id);conv.updated_at=now();await db.commit()
                status='ok'
                await emit('done','finish',200)
            except asyncio.CancelledError:
                status='cancelled';raise
            except Exception as exc:
                status='error'
                import logging
                logging.getLogger('knowgo.full').warning('Turn failed: %s',type(exc).__name__)
                import traceback
                from app.config import Settings
                diagnostic=traceback.format_exc()
                settings=Settings()
                for field in type(settings).model_fields:
                    value=getattr(settings,field)
                    if hasattr(value,'get_secret_value') and value.get_secret_value():diagnostic=diagnostic.replace(value.get_secret_value(),'[REDACTED]')
                with (PROJECT_ROOT/'logs/reference-errors.log').open('a') as output:output.write(json.dumps({'request_id':metrics.request_id,'conversation_id':str(cid),'error_type':type(exc).__name__,'time_utc':datetime.now(timezone.utc).isoformat()},ensure_ascii=False)+'\n'+diagnostic+'\n')
                message=exc.detail if isinstance(exc,HTTPException) else str(exc) if isinstance(exc,ValueError) else '本轮未完成，请重试；已保存的数据仍保留。'
                await emit('error',message,exc.status_code if isinstance(exc,HTTPException) else 500)
                await emit('done','finish',500)
            finally:
                var_child_runnable_config.reset(context_token)
                metrics.save(PROJECT_ROOT/'logs/full_request_metrics.jsonl',status=status)
                # 终版EventStream.close用哨兵结束迭代，异常及取消也必须关闭。
                stream.close()
        task=asyncio.create_task(worker());services.tasks.add(task);task.add_done_callback(services.tasks.discard)
        try:
            while True:
                try:event=await asyncio.wait_for(stream.__anext__(),15)
                except StopAsyncIteration:break
                except TimeoutError:yield ': keepalive\n\n';continue
                yield 'data: '+json.dumps(event,ensure_ascii=False)+'\n\n'
        finally:
            import anyio
            # 防止ASGI取消作用域反复取消gather，再次取消正在清理DB事务的worker。
            with anyio.CancelScope(shield=True):
                if not task.done():task.cancel()
                await asyncio.gather(task,return_exceptions=True)
    return StreamingResponse(events(),media_type='text/event-stream',headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

class ChatBody(BaseModel):
    conversation_id:UUID
    content:str=Field(min_length=1,max_length=6000,pattern=r'\S')

@router.post('/messages')
async def send_message(body:ChatBody,request:Request,user=Depends(current_user)):
    await authorize(request,body.conversation_id,user)
    return stream_turn(request,body.conversation_id,user,lambda emit:request.app.state.full.chat(str(body.conversation_id),user.id,body.content,emit))

@router.post('/conversations/{cid}/requirement')
async def requirement(cid:UUID,body:Requirement,request:Request,user=Depends(current_user)):
    await authorize(request,cid,user)
    return stream_turn(request,cid,user,lambda emit:request.app.state.full.start(str(cid),user.id,body.model_dump(mode='json'),emit))

class Submit(BaseModel):
    conversation_id:UUID
    card_id:UUID
    revision:int=Field(ge=0)
    selections:list[dict]=Field(max_length=12)

@router.post('/skills/{skill_name}/submit')
async def submit(skill_name:str,body:Submit,request:Request,user=Depends(current_user)):
    await authorize(request,body.conversation_id,user)
    async with request.app.state.full_db.session() as db:
        card=await db.get(Card,str(body.card_id))
        if card is None or card.conversation_id!=str(body.conversation_id) or card.skill_name!=skill_name:raise HTTPException(404,'卡片不存在')
        state=await request.app.state.full.state(str(body.conversation_id))
        if card.revision!=body.revision or state.get('revision')!=body.revision:raise HTTPException(409,'需求已更新，旧卡片不可提交')
        if card.submitted is None and card.expires_at<now():raise HTTPException(409,'候选已过期，请重新查询')
        if card.submitted is not None and card.submitted.get('selections')!=body.selections:raise HTTPException(409,'卡片已提交，修改选择请先回退')
        from app.full.capabilities import validate_selection
        try:validate_selection(card.payload,body.selections)
        except ValueError as exc:raise HTTPException(422,str(exc)) from None
    return stream_turn(request,body.conversation_id,user,lambda emit:request.app.state.full.submit(str(body.conversation_id),user.id,str(body.card_id),body.revision,body.selections,emit))

@router.get('/cards/{card_id}')
async def get_card(card_id:UUID,request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=await db.get(Card,str(card_id))
        if row is None:raise HTTPException(404,'卡片不存在')
        await owned(db,row.conversation_id,user.id)
        state=await request.app.state.full.state(row.conversation_id)
        return {'id':row.id,'revision':row.revision,'skill_name':row.skill_name,'data':{**row.payload,'default_selections':[{'segment_id':r['segment_id'],'option_id':r['option_id']} for r in state.get('selected_hotels' if row.skill_name=='hotel_multi_segment' else 'selected_transport',[])]},'submitted':row.submitted,'expires_at':row.expires_at.isoformat(),'is_current':row.revision==state.get('revision') and (row.submitted is not None or row.expires_at>now())}

@router.get('/plans')
async def plans(request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        rows=await db.scalars(select(Plan).join(Conversation).where(Conversation.user_id==user.id,Conversation.deleted_at.is_(None)).order_by(Plan.updated_at.desc()).limit(100))
        return {'items':[public(p) for p in rows]}

@router.get('/plans/{pid}')
async def plan(pid:UUID,request:Request,user=Depends(current_user)):
    async with request.app.state.full_db.session() as db:
        row=await db.get(Plan,str(pid))
        if row is None:raise HTTPException(404,'行程不存在')
        await owned(db,row.conversation_id,user.id)
        state=await request.app.state.full.state(row.conversation_id)
        from app.full.legacy_contract import plan_to_contract
        return {**public(row),'plan_data':plan_to_contract(row),'is_current':row.revision==state.get('revision')}

class MemoryBody(BaseModel):
    category:str
    operation:str=Field(pattern=r'^(append|replace|remove)$')
    values:list[str]=Field(max_length=30)

@router.get('/memory')
async def memory(request:Request,user=Depends(current_user)):return await request.app.state.full.memory(user.id)

@router.patch('/memory')
async def patch_memory(body:MemoryBody,request:Request,user=Depends(current_user)):
    try:return await request.app.state.full.memory_update(user.id,body.category,body.operation,body.values)
    except ValueError as exc:raise HTTPException(422,str(exc)) from None

class KnowledgeQuery(BaseModel):
    query:str=Field(min_length=1,max_length=500)
    city:str|None=None
    strategy:str=Field(default='multiquery',pattern=r'^(none|multiquery|hyde|rewrite|hybrid)$')
    rerank:bool=True

@router.post('/knowledge/search')
async def search(body:KnowledgeQuery,request:Request,user=Depends(current_user)):
    s=request.app.state.full
    return await s.knowledge.search(body.query,body.city,model=s.model,strategy=body.strategy,rerank=body.rerank)

@router.get('/knowledge/status')
async def status(request:Request,user=Depends(current_user)):return request.app.state.full.knowledge.status

@router.get('/cities')
async def cities(request:Request,q:str=''):
    from pathlib import Path
    cache=request.app.state.full.knowledge.redis
    key='kg:cities:cn:v1'
    try:raw=await cache.get(key) if cache else None
    except Exception:raw=None
    if raw:items=json.loads(raw)
    else:
        data=json.loads(Path(__file__).with_name('cities.json').read_text())
        items=[{'name':name,'province':province} for name,province in data.items()]
        if cache:
            try:await cache.set(key,json.dumps(items,ensure_ascii=False),ex=604800)
            except Exception:pass
    if q:items=[r for r in items if q in r['name'] or q in r['province']]
    return {'items':items,'total':len(items)}
