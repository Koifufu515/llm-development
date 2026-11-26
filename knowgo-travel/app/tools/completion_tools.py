import asyncio,json
from uuid import UUID
from langchain.tools import tool,ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from app.core.store import update_preferences
from app.services.contracts import PreferencePatch,PlanRequest
from app.services.planning import execute_plan
from app.core.telemetry import RequestMetrics
from app.config import PROJECT_ROOT


def make_completion_tools(model,manager,kb,store,user_id,remote=None):
    @tool
    async def remember_preferences(updates:PreferencePatch,runtime:ToolRuntime)->Command:
        """仅在用户明确要求记住/更新长期偏好时保存。用户未表达的字段不得猜测。"""
        if not user_id:text='当前会话未关联用户，请在完整规划页面创建用户后保存长期偏好。'
        else:
            saved=await update_preferences(store,user_id,updates.model_dump(exclude_unset=True))
            text='长期偏好已更新：'+json.dumps(saved,ensure_ascii=False)
        return Command(update={'messages':[ToolMessage(content=text,name='remember_preferences',tool_call_id=runtime.tool_call_id)]})

    @tool
    async def select_transport(option_id:str,runtime:ToolRuntime)->Command:
        """用户明确选择已展示车次后调用，必须传当前候选的option_id，不能代用户猜选。"""
        state=runtime.state
        row=next((x for x in state.get('transport_options',[]) if x['option_id']==option_id),None)
        if not state.get('requirement_confirmed') or row is None:
            return Command(update={'messages':[ToolMessage(content='选择失败，需求未确认或候选已过期，请重新查询。',tool_call_id=runtime.tool_call_id)]})
        return Command(update={'selected_transport':option_id,'current_step':'accommodation_planning',
            'messages':[ToolMessage(content='已选择'+row['train_code']+'，请用户提供每间房每晚与每人每天餐饮估算；实时酒店尚需供应商凭证，可在用户认可估算后生成行程。',tool_call_id=runtime.tool_call_id)]})

    @tool
    async def finalize_plan(hotel_per_night:float,meal_per_person_day:float,runtime:ToolRuntime)->Command:
        """用户明确同意用给定住宿/餐饮估算生成完整行程时调用。两个金额必须来自用户，不能编造。不会预订。"""
        state=runtime.state;req=state.get('user_requirement',{})
        if not state.get('selected_transport'):
            return Command(update={'messages':[ToolMessage(content='请先查询并明确选择交通候选。',tool_call_id=runtime.tool_call_id)]})
        sid=runtime.config['configurable']['thread_id']
        body=PlanRequest(session_id=UUID(sid),departure_city=req['departure_city'],departure_date=req['departure_date'],
            stops=[{'city':req['destination'],'days':req['travel_days']}],adults=req['adult_count'],children=req['children_count'],
            budget_per_person=req['budget_max'],hotel_per_night=hotel_per_night,meal_per_person_day=meal_per_person_day,
            auto_confirm=True,styles=req.get('travel_styles',[]))
        async def ignore(*args):pass
        metrics=RequestMetrics()
        try:
            prefs=await store.aget(('users',str(user_id),'preferences'),'profile') if user_id else None
            result=await execute_plan(body,manager,model,kb,prefs.value if prefs else {},metrics,ignore,selected_ids=[state['selected_transport']],remote=remote)
        except Exception:
            metrics.save(PROJECT_ROOT/'logs/planning_metrics.jsonl','failed')
            return Command(update={'messages':[ToolMessage(content='生成或查询校验失败，尚未生成成功行程，请重试或重新选择交通。',tool_call_id=runtime.tool_call_id)]})
        result['metrics']=metrics.save(PROJECT_ROOT/'logs/planning_metrics.jsonl')
        return Command(update={'current_step':'report_generation','planning_result':result,'itinerary':result['itinerary']['days'],
            'budget':result['budget'],'report':result['itinerary']['summary'],
            'messages':[ToolMessage(content=json.dumps(result,ensure_ascii=False),tool_call_id=runtime.tool_call_id)]})
    @tool
    async def query_hotels(city:str,date:str,nights:int,adults:int=1)->str:
        """查询真实酒店候选，需明确城市、入住日期、晚数与每间房成人数；不得声称已经预订。"""
        from app.services.remote import hotels
        if not remote:return '酒店服务未配置'
        return json.dumps(await hotels(remote,city,date,nights,adults),ensure_ascii=False)

    @tool
    async def query_flights(date:str,departure_airport:str,arrival_airport:str)->str:
        """查询真实航班时刻。必须先明确实际机场，再使用机场IATA三字码，城市有多个机场时先澄清，不擅自选机场。返回未知价格不代表免费。"""
        from app.services.remote import flight_schedule
        if not remote:return '航班服务未配置'
        return json.dumps(await flight_schedule(remote,date,departure_airport,arrival_airport),ensure_ascii=False)

    @tool
    async def query_driving(departure:str,destination:str)->str:
        """用高德查询两地驾车路线，城市级输入表示中心点路线，不承诺精确到用户住址或总油费。"""
        from app.services.remote import amap_driving
        if not remote:return '地图服务未配置'
        return json.dumps(await amap_driving(remote,departure,destination),ensure_ascii=False)
    return [remember_preferences,select_transport,finalize_plan,query_hotels,query_flights,query_driving]
