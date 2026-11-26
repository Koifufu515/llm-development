import asyncio
import json
from uuid import UUID,uuid4
from fastapi import APIRouter,HTTPException,Request
from fastapi.responses import StreamingResponse,FileResponse
from pydantic import BaseModel,Field
from app.config import Settings,PROJECT_ROOT
from app.core.store import update_preferences
from app.core.telemetry import RequestMetrics
from app.core.transitions import requirement_update
from app.core.state import RequirementPatch
from app.services.contracts import PlanRequest,PreferencePatch,SelectionRequest
from app.services.planning import execute_plan
from app.utils.llm_factory import get_deepseek_llm

router=APIRouter()

class SearchRequest(BaseModel):
    query:str=Field(min_length=1,max_length=500)
    city:str | None=Field(default=None,max_length=80)
    rerank:bool=True

@router.post('/api/users',status_code=201)
async def create_user(request:Request):
    user_id=str(uuid4())
    await request.app.state.store.aput(('users',),'registered:'+user_id,{'user_id':user_id})
    return {'user_id':user_id,'scope':'local_demo'}

async def require_user(request,user_id):
    if not await request.app.state.store.aget(('users',),'registered:'+str(user_id)):
        raise HTTPException(404,'用户不存在')

@router.get('/api/users/{user_id}/preferences')
async def read_preferences(user_id:UUID,request:Request):
    await require_user(request,user_id)
    item=await request.app.state.store.aget(('users',str(user_id),'preferences'),'profile')
    return item.value if item else {}

@router.patch('/api/users/{user_id}/preferences')
async def patch_preferences(user_id:UUID,body:PreferencePatch,request:Request):
    await require_user(request,user_id)
    return await update_preferences(request.app.state.store,user_id,body.model_dump(exclude_unset=True))

@router.post('/api/knowledge/search')
async def knowledge_search(body:SearchRequest,request:Request):
    return await asyncio.to_thread(request.app.state.knowledge.search,body.query,body.city,5,body.rerank)

@router.get('/api/knowledge/status')
async def knowledge_status(request:Request):
    kb=request.app.state.knowledge
    return {'parents':len(kb.parents),'children':len(kb.children),'version':kb.version,'embedding':'BAAI/bge-small-zh-v1.5','reranker':'词项覆盖率（非cross-encoder）'}

async def run_plan(body,request,emit,selected_ids=None,source_revision=None,submission_key=None):
    from app.main import read_session
    settings=Settings()
    if not settings.model_configured:raise HTTPException(503,'请在本机配置模型凭证')
    metrics=RequestMetrics()
    async with request.app.state.write_lock:
        previous=await read_session(body.session_id)
        if source_revision is not None and source_revision!=previous.get('requirement_revision',0):
            raise HTTPException(409,'需求版本已变更，请重新查询和选择')
        if submission_key:
            cached=await request.app.state.store.aget(('submissions',str(body.session_id)),submission_key)
            if cached:return cached.value
        req={'departure_city':body.departure_city,'destination':body.stops[0].city,'departure_date':body.departure_date.isoformat(),
             'travel_days':sum(s.days for s in body.stops),'adult_count':body.adults,'children_count':body.children,
             'budget_max':body.budget_per_person,'travel_styles':body.styles}
        update=requirement_update(previous,RequirementPatch(**req),force=bool(previous.get('planning_stops')) and previous['planning_stops']!=[s.model_dump() for s in body.stops])
        revision=update.get('requirement_revision',previous.get('requirement_revision',0))
        config={'configurable':{'thread_id':str(body.session_id)}}
        await request.app.state.state_reader.aupdate_state(config,{**update,'requirement_confirmed':body.auto_confirm,
            'confirmed_revision':revision if body.auto_confirm else None,'current_step':'transport_planning','planning_stops':[s.model_dump() for s in body.stops]},as_node='read_only')
        meta=await request.app.state.store.aget(('sessions',),str(body.session_id))
        prefs={}
        if meta and meta.value.get('user_id'):
            item=await request.app.state.store.aget(('users',meta.value['user_id'],'preferences'),'profile')
            prefs=item.value if item else {}
        try:
            result=await asyncio.wait_for(execute_plan(body,request.app.state.mcp_manager,get_deepseek_llm(settings),request.app.state.knowledge,prefs,metrics,emit,selected_ids=selected_ids,remote=request.app.state.remote),240)
            update={'transport_options':[o for seg in result['segments'] for o in seg.get('options',[])],
                    'accommodation_options':result['accommodation'],'planning_result':result}
            if result['status']=='completed':
                update.update({'itinerary':result['itinerary']['days'],'budget':result['budget'],'report':result['itinerary']['summary'],
                    'current_step':'report_generation'})
            await request.app.state.state_reader.aupdate_state(config,update,as_node='read_only')
            plan_id=str(uuid4())
            result.update({'plan_id':plan_id,'session_id':str(body.session_id),'revision':revision,'metrics':metrics.save(PROJECT_ROOT/'logs/planning_metrics.jsonl'),'request':body.model_dump(mode='json')})
            await request.app.state.store.aput(('plans',str(body.session_id)),plan_id,result)
            if submission_key:await request.app.state.store.aput(('submissions',str(body.session_id)),submission_key,result)
            return result
        except BaseException:
            metrics.save(PROJECT_ROOT/'logs/planning_metrics.jsonl','failed_or_cancelled')
            raise

@router.post('/api/plans')
async def plan(body:PlanRequest,request:Request):
    async def ignore(*args):pass
    return await run_plan(body,request,ignore)

@router.post('/api/plans/stream')
async def stream_plan(body:PlanRequest,request:Request):
    # 每次连接独立队列；断连取消本次任务，不向共享会话发送其他请求的事件。
    from app.main import read_session
    await read_session(body.session_id)
    async def events():
        queue=asyncio.Queue(maxsize=32)
        async def emit(kind,data):await queue.put((kind,data))
        async def worker():
            try:await emit('result',await run_plan(body,request,emit))
            except asyncio.CancelledError:raise
            except Exception as exc:
                detail=exc.detail if isinstance(exc,HTTPException) else '规划失败：模型、数据源或结构校验未通过，请重试。'
                await emit('error',{'message':detail})
            finally:await queue.put(('done',{}))
        task=asyncio.create_task(worker())
        try:
            while True:
                try:kind,data=await asyncio.wait_for(queue.get(),15)
                except TimeoutError:
                    yield ': keepalive\n\n';continue
                yield 'event: '+kind+'\ndata: '+json.dumps(data,ensure_ascii=False)+'\n\n'
                if kind=='done':break
        finally:
            task.cancel()
            await asyncio.gather(task,return_exceptions=True)
    return StreamingResponse(events(),media_type='text/event-stream',headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

@router.get('/api/sessions/{session_id}/plans')
async def list_plans(session_id:UUID,request:Request):
    from app.main import read_session
    await read_session(session_id)
    rows=await request.app.state.store.asearch(('plans',str(session_id)),limit=30)
    return {'plans':[r.value for r in rows]}

@router.post('/api/sessions/{session_id}/transport/select')
async def select_transport(session_id:UUID,body:SelectionRequest,request:Request):
    from app.main import read_session
    async with request.app.state.write_lock:
        state=await read_session(session_id)
        if body.revision!=state.get('requirement_revision') or not state.get('requirement_confirmed'):
            raise HTTPException(409,'需求未确认或版本已变更，请重新查询')
        if state.get('current_step') not in {'transport_planning','accommodation_planning'}:
            raise HTTPException(409,'当前步骤不能选择交通，请先修改需求或重新规划')
        row=next((o for o in state.get('transport_options',[]) if o['option_id']==body.option_id),None)
        if row is None:raise HTTPException(422,'候选已过期或不属于当前会话')
        if state.get('selected_transport')==body.option_id:
            return {'selected':row,'current_step':state['current_step']}
        await request.app.state.state_reader.aupdate_state({'configurable':{'thread_id':str(session_id)}},
            {'selected_transport':body.option_id,'current_step':'accommodation_planning'},as_node='read_only')
        return {'selected':row,'current_step':'accommodation_planning'}

@router.get('/studio',include_in_schema=False)
async def studio():return FileResponse(PROJECT_ROOT/'app/static/studio.html')

class DispatchRequest(BaseModel):
    session_id:UUID
    message:str=Field(min_length=1,max_length=4000)

@router.post('/api/chat/dispatch')
async def dispatch(body:DispatchRequest,request:Request):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.services.routing import classify
    from app.services.providers import query_rail
    from app.mcp_core.servers.weather_data import safely_query,query_weather
    from app.main import read_session,chat,ChatRequest
    previous=await read_session(body.session_id)
    metrics=RequestMetrics()
    try:
        route=await classify(get_deepseek_llm(Settings()),body.message,metrics,datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat())
        data=None
        if route.channel=='direct':
            req=previous.get('user_requirement',{})
            if route.intent=='weather':
                city=route.city or route.destination or req.get('destination')
                data=await safely_query(query_weather,city,route.date) if city else {'status':'missing_fields','message':'请说明查询哪个城市'}
            elif route.intent=='rail':
                leg={'leg_id':'direct','fromStation':route.departure_city or req.get('departure_city'),
                     'toStation':route.destination or req.get('destination'),'date':route.date or req.get('departure_date')}
                data=await query_rail(request.app.state.mcp_manager,leg)
            return {'route':route.model_dump(),'data':data,'metrics':metrics.save(PROJECT_ROOT/'logs/routing_metrics.jsonl')}
        result=await chat(ChatRequest(session_id=body.session_id,message=body.message))
        return {'route':route.model_dump(),'data':result,'metrics':metrics.save(PROJECT_ROOT/'logs/routing_metrics.jsonl')}
    except Exception:
        metrics.save(PROJECT_ROOT/'logs/routing_metrics.jsonl','failed')
        raise

@router.get('/api/providers/status')
async def provider_status():
    s=Settings()
    return {'model_provider':s.model_provider,'qwen_configured':bool(s.dashscope_api_key.get_secret_value()),
            'amap_configured':bool(s.amap_api_key.get_secret_value()),'tencent_configured':bool(s.tencent_map_key.get_secret_value()),
            'flight_configured':bool(s.variflight_api_key.get_secret_value()),'hotel_configured':bool(s.aigohotel_mcp_api.get_secret_value()),
            'rail':'无需Key；12306 MCP'}

@router.get('/api/providers/{service}/tools')
async def provider_tools(service:str,request:Request):
    if service not in {'hotel','flight','amap'}:raise HTTPException(404,'未知服务')
    tools=await request.app.state.remote.discover(service)
    return {'status':'ready' if tools else 'unavailable','tools':[{'name':t.name,'schema':t.args_schema if isinstance(t.args_schema,dict) else t.args_schema.model_json_schema()} for t in tools]}

class HotelSearch(BaseModel):
    city:str=Field(min_length=1,max_length=80)
    date:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    nights:int=Field(ge=1,le=30)
    adults:int=Field(default=1,ge=1,le=10)

@router.post('/api/hotels/search')
async def hotel_search(body:HotelSearch,request:Request):
    from app.services.remote import hotels
    return await hotels(request.app.state.remote,body.city,body.date,body.nights,body.adults)

class FlightSearch(BaseModel):
    date:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    departure_airport:str=Field(pattern=r'^[A-Z]{3}$')
    arrival_airport:str=Field(pattern=r'^[A-Z]{3}$')

@router.post('/api/flights/search')
async def flights_search(body:FlightSearch,request:Request):
    from app.services.remote import flight_schedule
    return await flight_schedule(request.app.state.remote,body.date,body.departure_airport,body.arrival_airport)

class DrivingSearch(BaseModel):
    departure:str=Field(min_length=1,max_length=80)
    destination:str=Field(min_length=1,max_length=80)

@router.post('/api/driving/search')
async def driving_search(body:DrivingSearch):
    from app.services.remote import driving_route
    return await driving_route(body.departure,body.destination)

@router.post('/api/driving/amap')
async def amap_driving_search(body:DrivingSearch,request:Request):
    from app.services.remote import amap_driving
    return await amap_driving(request.app.state.remote,body.departure,body.destination)

class PlanSelection(BaseModel):
    session_id:UUID
    revision:int=Field(ge=0)
    option_ids:list[str]=Field(max_length=5)

@router.post('/api/plans/{plan_id}/submit')
async def submit_plan(plan_id:UUID,body:PlanSelection,request:Request):
    import hashlib
    item=await request.app.state.store.aget(('plans',str(body.session_id)),str(plan_id))
    if item is None:raise HTTPException(404,'计划不存在或不属于当前会话')
    plan=item.value
    if plan['revision']!=body.revision:raise HTTPException(409,'候选版本已过期')
    if len(body.option_ids)!=len(plan['segments']):raise HTTPException(422,'请为每一交通段选择候选')
    for option_id,segment in zip(body.option_ids,plan['segments']):
        if not any(o['option_id']==option_id for o in segment.get('options',[])):
            raise HTTPException(422,'选项不属于当前交通段')
    payload=PlanRequest.model_validate({**plan['request'],'auto_confirm':True})
    key=str(plan_id)+':'+hashlib.sha256(json.dumps(body.option_ids).encode()).hexdigest()
    async def ignore(*args):pass
    return await run_plan(payload,request,ignore,body.option_ids,body.revision,key)
