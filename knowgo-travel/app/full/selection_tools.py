"""原0395/0399/0402逐段/逐城选择，接入同一真实卡片候选与回执。
保留原工具语义，修复模型可自行填价格的问题：报价、时刻以已查询候选为准。
"""
import json
from pydantic import BaseModel
from langchain.tools import tool,ToolRuntime
from langgraph.types import Command
from app.full.database import Card,now,owned
from app.full.capabilities import available
from app.full.agent import reply
class LegChoice(BaseModel):
    from_city:str
    to_city:str
    vehicle_no:str
    depart_time:str=''
    arrive_time:str=''
    seat_class:str=''
    price:float|None=None

def next_segment(payload,picked):
    done={r['segment_id'] for r in picked}
    return next((s for s in payload['segments'] if s['segment_id'] not in done and any(o.get('mode',payload.get('mode'))!='train' or available(o.get('availability')) for o in s.get('options',[]))),None)

def match_transport(segment,choice):
    if choice.from_city.rstrip('市')!=segment['from'].rstrip('市') or choice.to_city.rstrip('市')!=segment['to'].rstrip('市'):
        raise ValueError('当前应确认'+segment['from']+'→'+segment['to']+'，不接受其他路段')
    candidates=[o for o in segment['options'] if (o.get('mode','train')!='train' or available(o.get('availability'))) and (choice.vehicle_no.upper() in (str(o.get('train_code') or o.get('flight_code') or '').upper(),str(o['name']).upper()) or o.get('mode')=='driving' and choice.vehicle_no in ('自驾','开车','驾车')) and (not choice.seat_class or choice.seat_class in str(o.get('seat_type') or o['name']))]
    if len(candidates)!=1:raise ValueError('未唯一匹配真实可用候选，请明确卡片中的班次和席别，禁止自行编票价')
    return candidates[0]

def match_hotel(segment,text):
    if segment['city'] not in text:raise ValueError('当前应确认'+segment['city']+'的住宿，其他城市不写入')
    candidates=[o for o in segment['options'] if str(o['name']).split('（')[0] in text]
    if len(candidates)!=1:raise ValueError('未唯一匹配该城市已展示的酒店或品牌，请使用卡片原名称')
    return candidates[0]

async def select_from_card(services,user_id,runtime,kind,values,expected_mode=None):
    state=runtime.state;expected='transport_planning' if kind=='transport' else 'accommodation_planning'
    if state.get('current_step')!=expected:raise ValueError('当前阶段不接受该选择')
    cid=runtime.config['configurable']['thread_id'];active=state.get('active_card') or {}
    async with services.db.session() as db:
        await owned(db,cid,user_id);card=await db.get(Card,active.get('id')) if active.get('id') else None
        if card is None or card.conversation_id!=cid:raise ValueError('请先查询并展示真实候选卡片')
        if card.revision!=state.get('revision') or card.expires_at<now() or card.submitted is not None:raise ValueError('候选已变更、过期或提交，请使用当前卡片')
        if (card.skill_name=='hotel_multi_segment')!=(kind=='hotel'):raise ValueError('候选卡片类型不符')
        field='selected_transport' if kind=='transport' else 'selected_hotels';picked=list(state.get(field) or [])
        # 先在本地验证整批，任何一条错误都不写入部分选择。
        for value in values:
            segment=next_segment(card.payload,picked)
            if segment is None:raise ValueError('所有路段/站点已确认，不接受额外选择')
            option=match_transport(segment,value) if kind=='transport' else match_hotel(segment,value)
            if kind=='transport' and expected_mode and option.get('mode')!=expected_mode:raise ValueError('所选方式与真实候选不一致')
            picked.append(option)
        complete=next_segment(card.payload,picked) is None
        if not values and not complete:raise ValueError('未提供选择；不能凭空确认尚未选择的候选')
        if complete:
            card.submitted={'selections':[{'segment_id':p['segment_id'],'option_id':p['option_id']} for p in picked],'confirmed_at':now().isoformat()};await db.commit()
        return {field:picked,'active_card':None if complete else active,'current_step':('accommodation_planning' if kind=='transport' else 'food_planning') if complete else expected}

def changed_accommodation(state,types):
    if state.get('requirement',{}).get('accommodation_types')==types:return None
    from app.full.agent import reset_after
    from app.full.domain import Requirement
    req=Requirement.model_validate({**state['requirement'],'accommodation_types':types})
    revision=state.get('revision',0)+1
    return {**reset_after('accommodation_planning'),'requirement':req.model_dump(mode='json'),'revision':revision,'confirmed_revision':revision,'current_step':'accommodation_planning'}

def build_selection_tools(services,user_id):
    @tool(return_direct=True)
    async def select_transport_tool(transport_type:str,legs:list[LegChoice]|None=None,runtime:ToolRuntime=None)->Command:
        """按原流程逐段确认交通；legs仅当前待确认段，班次和席别须来自已展示卡片，真实价格时刻以候选为准。"""
        if transport_type not in ('train','flight','driving'):return reply(runtime,'交通方式无效')
        try:updates=await select_from_card(services,user_id,runtime,'transport',legs or [],transport_type)
        except ValueError as exc:return reply(runtime,str(exc))
        return reply(runtime,'已从真实候选确认该段交通，继续未完成路段。',**updates)
    @tool(return_direct=True)
    async def select_accommodation_tool(accommodation_types:list[str],hotels:list[str]|None=None,runtime:ToolRuntime=None)->Command:
        """逐城确认已展示酒店/品牌；hotels须含当前城市和卡片原名称，全部城市完成后再推进餐饮。"""
        if not accommodation_types or set(accommodation_types)-{'star_hotel','economy_hotel','hostel','youth_hostel'}:return reply(runtime,'住宿类型无效')
        changed=changed_accommodation(runtime.state,accommodation_types)
        if changed:return reply(runtime,'住宿类型已调整，先重查相应真实候选；旧卡片不再确认。',**changed)
        try:updates=await select_from_card(services,user_id,runtime,'hotel',hotels or [])
        except ValueError as exc:return reply(runtime,str(exc))
        return reply(runtime,'该城市住宿已确认。',**updates)
    @tool(return_direct=True)
    async def select_accommodation_food_tool(accommodation_types:list[str],food_types:list[str],hotels:list[str]|None=None,runtime:ToolRuntime=None)->Command:
        """一次Command合并住宿与餐饮选择，避免同轮并行Command冲突；住宿仍逐城核对真实卡片。"""
        if not accommodation_types or set(accommodation_types)-{'star_hotel','economy_hotel','hostel','youth_hostel'} or not food_types or set(food_types)-{'local','specialty','chain'}:return reply(runtime,'住宿或餐饮类型无效')
        changed=changed_accommodation(runtime.state,accommodation_types)
        if changed:
            changed['food_preferences']=food_types
            return reply(runtime,'住宿类型和餐饮已合并记录，先重查酒店候选。',**changed)
        try:updates=await select_from_card(services,user_id,runtime,'hotel',hotels or [])
        except ValueError as exc:return reply(runtime,str(exc))
        return reply(runtime,'住宿与餐饮已合并记录。',**updates,food_preferences=food_types)
    return [select_transport_tool,select_accommodation_tool,select_accommodation_food_tool]
