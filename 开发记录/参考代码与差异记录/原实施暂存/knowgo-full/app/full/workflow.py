import asyncio,json,re
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel

from app.full.agent import FullState,make_agent,reset_after,CLEAR
from app.full.domain import Requirement,topology,budget,STEPS
from app.full.database import Conversation,Message,Card,Plan,now,owned
from app.full.capabilities import transport_payload,hotel_payload,auto_pick,validate_selection
from app.full.destination import build_destination_graph
from app.full.plans import generate,render,enrich_map
from app.full.knowledge import AdvancedKnowledge
from app.utils.llm_factory import get_deepseek_llm
from app.config import Settings
from app.core.telemetry import RequestMetrics

class DestinationPick(BaseModel):
    city:str
    reason:str

class Services:
    def __init__(self,app):
        self.app=app;self.db=app.state.full_db;self.store=app.state.store;self.checkpointer=app.state.checkpointer
        self.model=get_deepseek_llm(Settings());self.remote=app.state.remote;self.mcp_manager=app.state.mcp_manager
        self.knowledge=AdvancedKnowledge();self.tasks=set()
        g=StateGraph(FullState);g.add_node('read_only',lambda state:{});g.add_edge(START,'read_only');g.add_edge('read_only',END)
        self.reader=g.compile(checkpointer=self.checkpointer)
        self.destination_graph=build_destination_graph(self)
    async def close(self):
        for task in list(self.tasks):task.cancel()
        await asyncio.gather(*self.tasks,return_exceptions=True)
        await self.knowledge.close()
    def config(self,cid):return {'configurable':{'thread_id':str(cid)}}
    async def state(self,cid):return (await self.reader.aget_state(self.config(cid))).values
    async def write(self,cid,updates):await self.reader.aupdate_state(self.config(cid),updates,as_node='read_only')
    async def destination(self,city,question):
        state=await self.destination_graph.ainvoke({'city':city,'question':question,'reports':[]})
        return {k:state[k] for k in ('city','summary','reports')}
    async def memory(self,user_id):
        row=await self.store.aget(('full_users',user_id),'memory')
        return row.value if row else {}
    async def memory_update(self,user_id,category,operation,values):
        valid={'travel_styles','dietary_restrictions','food_preferences','accommodation_preferences','travel_history'}
        if category not in valid or operation not in ('append','replace','remove'):raise ValueError('记忆类别或操作无效')
        if len(values)>30 or any(len(v)>500 for v in values):raise ValueError('记忆条目过长')
        if any('过敏' in v or '饮食禁忌' in v for v in values):category='dietary_restrictions'
        async with self.db.lock('memory:'+user_id):
            old=await self.memory(user_id);before=old.get(category,[])
            after=list(dict.fromkeys([*before,*values])) if operation=='append' else list(dict.fromkeys(values)) if operation=='replace' else [v for v in before if v not in values]
            merged={**old,category:after};await self.store.aput(('full_users',user_id),'memory',merged)
            return merged
    async def save_message(self,cid,role,content,extra=None):
        async with self.db.session() as db:
            db.add(Message(conversation_id=cid,role=role,content=content,extra=extra or {}));await db.commit()
    async def card(self,cid,req,payload):
        state=await self.state(cid);active=state.get('active_card')
        async with self.db.session() as db:
            if active:
                old=await db.get(Card,active['id'])
                if old and old.revision==state.get('revision',0) and old.submitted is None and old.expires_at>now() and old.skill_name==payload['skill_name']:
                    return {'id':old.id,'revision':old.revision,'data':old.payload,'skill_name':old.skill_name,'expires_at':old.expires_at.isoformat()}
            row=Card(conversation_id=cid,skill_name=payload['skill_name'],revision=state.get('revision',0),payload=payload,expires_at=now()+timedelta(minutes=10))
            db.add(row);await db.commit()
            result={'id':row.id,'revision':row.revision,'data':payload,'skill_name':row.skill_name,'expires_at':row.expires_at.isoformat()}
        await self.write(cid,{'active_card':{'id':result['id'],'skill_name':result['skill_name']}})
        return result
    async def existing_card(self,cid,skill):
        state=await self.state(cid);active=state.get('active_card')
        if not active:return None
        async with self.db.session() as db:
            row=await db.get(Card,active['id'])
            if row and row.skill_name==skill and row.revision==state.get('revision',0) and row.submitted is None and row.expires_at>now():
                return {'id':row.id,'revision':row.revision,'skill_name':skill,'data':row.payload,'expires_at':row.expires_at.isoformat()}
        return None
    async def start(self,cid,user_id,data,emit):
        req=Requirement.model_validate(data);state=await self.state(cid)
        await self.write(cid,{'user_id':user_id,'requirement':req.model_dump(mode='json'),'revision':state.get('revision',0)+1,
         'confirmed_revision':None,'current_step':'destination_recommendation',**reset_after('destination_recommendation')})
        await self.save_message(cid,'user','提交旅行需求',{'requirement':req.model_dump(mode='json')})
        return await self.advance(cid,user_id,emit)
    async def advance(self,cid,user_id,emit):
        extra={};texts=[]
        for _ in range(8):
            state=await self.state(cid);step=state.get('current_step','requirement_collection')
            if step=='requirement_collection':return {'text':'请补充出发地、日期、天数、人数和预算，或使用旅行需求表单。','extra':extra}
            req=Requirement.model_validate(state['requirement'])
            if step=='destination_recommendation':
                if not req.destinations:
                    pick=await self.model.with_structured_output(DestinationPick).ainvoke('为以下需求推荐一个中国境内城市，返回city和reason，不要臆造城市。'+json.dumps(req.model_dump(mode='json'),ensure_ascii=False))
                    if not pick.city or len(pick.city)>20:raise ValueError('未取得合法目的地')
                    req=req.model_copy(update={'destinations':[pick.city]})
                    await self.write(cid,{'requirement':req.model_dump(mode='json')})
                    texts.append('推荐目的地：'+pick.city+'。'+pick.reason)
                if not req.auto_confirm and state.get('confirmed_revision')!=state.get('revision',0):
                    info=state.get('destination_info')
                    if info is None:
                        await emit('skills',{'skill_name':'destination','title':'查询目的地','desc':'攻略与天气并行'})
                        infos=await asyncio.gather(*(self.destination(city,'目的地概况与景点') for city in req.destinations))
                        info={'destinations':infos};await self.write(cid,{'destination_info':info})
                    text='\n\n'.join([*texts,*[i['summary'] for i in info['destinations']],
                      f"请确认：{req.departure_city} → {' → '.join(req.destinations)} → {req.departure_city}，{req.departure_date}出发，共{req.travel_days}天、{req.adult_count}成人{req.children_count}儿童。回复“确认”后查询交通。"])
                    extra['destination_info']=info;return {'text':text,'extra':extra}
                await self.write(cid,{'current_step':'transport_planning','confirmed_revision':state.get('revision',0)})
                if req.auto_confirm:
                    from app.mcp_core.servers.weather_data import safely_query,query_weather
                    await emit('skills',{'skill_name':'express','title':'并行收集旅行资料','desc':'各段交通、各站住宿与各城天气同时查询'})
                    tp,hp,*weather=await asyncio.gather(transport_payload(self,req),hotel_payload(self,req),
                        *(safely_query(query_weather,city,req.departure_date.isoformat()) for city in req.destinations))
                    selected_transport=validate_selection(tp,auto_pick(tp));selected_hotels=validate_selection(hp,auto_pick(hp))
                    extra['weather']=dict(zip(req.destinations,weather))
                    extra['transport_status']=[{k:s.get(k) for k in ('segment_id','from','to','date','status','message')} for s in tp['segments']]
                    await self.write(cid,{'selected_transport':selected_transport,'selected_hotels':selected_hotels,
                       'food_preferences':req.food_preferences or ['local','specialty'],'current_step':'itinerary_generation'})
                    texts.extend('交通：'+p['from']+'→'+p['to']+' '+p['name'] for p in selected_transport)
                    texts.extend('住宿：'+p['city']+' '+p['name']+('（品牌参考，无实时报价）' if p['mode']=='brand' else '') for p in selected_hotels)
                    missing=[s for s in tp['segments'] if s['segment_id'] not in {p['segment_id'] for p in selected_transport}]
                    if missing:texts.append('实时查询未取得候选的路段：'+'、'.join(s['from']+'→'+s['to'] for s in missing)+'；相关费用已明确按估算列出。')
            elif step=='transport_planning':
                if not topology(req)['legs']:
                    await self.write(cid,{'selected_transport':[],'current_step':'accommodation_planning'});texts.append('本次为本地游，无需城际交通。');continue
                skill=req.transport_types[0]+'_multi_segment';card=await self.existing_card(cid,skill)
                await emit('skills',{'skill_name':skill,'title':'查询各段交通','desc':'含去程、转场与返程，并行查询'})
                payload=card['data'] if card else await transport_payload(self,req)
                if req.auto_confirm:
                    choices=auto_pick(payload);picked=validate_selection(payload,choices)
                    await self.write(cid,{'selected_transport':picked,'active_card':None,'current_step':'accommodation_planning'})
                    texts.extend('交通：'+p['from']+'→'+p['to']+' '+p['name'] for p in picked)
                    missing=[s for s in payload['segments'] if s['segment_id'] not in {p['segment_id'] for p in picked}]
                    if missing:texts.append('以下路段实时数据不可用，行程中保留待核实并估算费用：'+'、'.join(s['from']+'→'+s['to'] for s in missing))
                else:
                    card=card or await self.card(cid,req,payload);await emit('skill_ui',card);extra['skill_ui']=card
                    return {'text':'已查询各段交通，请在卡片中逐段选择后提交。无候选路段会明确标记。','extra':extra}
            elif step=='accommodation_planning':
                if not topology(req)['stays']:
                    await self.write(cid,{'selected_hotels':[],'current_step':'food_planning'});continue
                await emit('skills',{'skill_name':'hotel_multi_segment','title':'查询各站住宿','desc':'按入住窗口并行，门店不可用时提供品牌参考'})
                card=await self.existing_card(cid,'hotel_multi_segment');payload=card['data'] if card else await hotel_payload(self,req)
                if req.auto_confirm:
                    picked=validate_selection(payload,auto_pick(payload))
                    await self.write(cid,{'selected_hotels':picked,'active_card':None,'current_step':'food_planning'})
                    texts.extend('住宿：'+p['city']+' '+p['name']+('（品牌参考，无实时报价）' if p['mode']=='brand' else '') for p in picked)
                else:
                    card=card or await self.card(cid,req,payload);await emit('skill_ui',card);extra['skill_ui']=card
                    return {'text':'请为各站选择住宿；品牌参考没有具体门店报价。','extra':extra}
            elif step=='food_planning':
                food=state.get('food_preferences') or req.food_preferences
                if not food and not req.auto_confirm:return {'text':'请选择餐饮偏好：特色美食、本地小吃或连锁快餐（可多选）。','extra':extra}
                await self.write(cid,{'food_preferences':food or ['local','specialty'],'current_step':'itinerary_generation'})
            elif step=='itinerary_generation':
                picked=state.get('selected_transport',[]);hotels=state.get('selected_hotels',[])
                req=req.model_copy(update={'food_preferences':state.get('food_preferences',req.food_preferences)})
                body,sources=await generate(self,req,picked,hotels,await self.memory(user_id),emit)
                costs=budget(req,picked,hotels)
                await emit('itinerary_plans',{'status':'pending','message':'正在保存行程清单并核对地图地点'})
                try:mapdata=await asyncio.wait_for(enrich_map(self,body),90)
                except Exception:mapdata={'status':'unavailable','points':[]}
                mapdata['sources']=[{k:r.get(k) for k in ('id','city','title','source_url','license','freshness')} for r in sources]
                async with self.db.session() as db:
                    plan=await db.scalar(select(Plan).where(Plan.conversation_id==cid))
                    if plan is None:plan=Plan(conversation_id=cid);db.add(plan)
                    plan.title=body['title'];plan.revision=state.get('revision',0);plan.body=body;plan.budget=costs;plan.map_data=mapdata
                    await db.commit();pid=plan.id
                await self.write(cid,{'itinerary_body':body,'budget':costs,'plan_id':pid,'current_step':'budget_summarization','active_card':None})
                from app.full.quality import schedule_quality
                schedule_quality(self,pid,req,body,picked,sources,hotels,costs,await self.memory(user_id),revision=state.get('revision',0))
                info={'status':'success','id':pid,'message':'行程清单已生成'};await emit('itinerary_plans',info)
                extra.update({'itinerary_plans':info,'sources':sources,'selected_transport':picked,'selected_hotels':hotels})
                return {'text':'\n'.join(texts)+'\n\n'+render(body,costs,sources),'extra':extra}
            else:return {'text':'行程已保存。如需调整天数、目的地、交通或住宿，直接告诉我。','extra':extra}
        raise RuntimeError('流程推进超过上限')

    async def submit(self,cid,user_id,card_id,revision,selections,emit):
        state=await self.state(cid)
        async with self.db.session() as db:
            card=await db.get(Card,card_id)
            if card is None or card.conversation_id!=cid:raise ValueError('卡片不存在')
            if revision!=state.get('revision') or card.revision!=revision:raise ValueError('需求已更新，旧卡片不可提交')
            repeated=card.submitted is not None
            if repeated and card.submitted.get('selections')!=selections:raise ValueError('卡片已提交，修改选择请先回退')
            if not repeated and card.expires_at<now():raise ValueError('候选已过期，请重新查询')
            skill=card.skill_name;expected='accommodation_planning' if skill=='hotel_multi_segment' else 'transport_planning'
            picked=validate_selection(card.payload,selections)
            nextstep='food_planning' if expected=='accommodation_planning' else 'accommodation_planning'
            if not repeated and state.get('current_step')!=expected:raise ValueError('当前步骤不接受该卡片')
            # 先持久化选择回执，checkpoint写失败时同请求可恢复，不跨两个独立事务假装原子提交。
            if not repeated:
                card.submitted={'selections':selections,'confirmed_at':now().isoformat()};await db.commit()
            if state.get('current_step')==expected:
                await self.write(cid,{'selected_hotels' if expected=='accommodation_planning' else 'selected_transport':picked,'active_card':None,'current_step':nextstep})
            # 更新持久消息卡片回放态，不依赖进程内缓存。
            messages=(await db.scalars(select(Message).where(Message.conversation_id==cid,Message.role=='assistant').order_by(Message.created_at.desc()).limit(30))).all()
            for message in messages:
                ui=message.extra.get('skill_ui')
                if ui and ui.get('id')==card_id:
                    message.extra={**message.extra,'skill_ui':{**ui,'submitted':card.submitted}};break
            await db.commit()
        if repeated and state.get('current_step')=='budget_summarization':
            return {'text':'该选择已保存，无需重复提交。','extra':{'idempotent':True}}
        await emit('assistant',('已恢复已保存的选择：' if repeated else '已确认：')+'；'.join(p['name'] for p in picked)+'。\n')
        return await self.advance(cid,user_id,emit)

    async def chat(self,cid,user_id,content,emit):
        await self.save_message(cid,'user',content)
        state=await self.state(cid);metrics=RequestMetrics()
        from app.full.routing import direct_query,route
        direct=await direct_query(self,cid,content,emit)
        if direct is not None:return direct
        async with self.db.session() as db:
            rows=(await db.scalars(select(Message).where(Message.conversation_id==cid).order_by(Message.created_at.desc()).limit(5))).all()
            history=[r.role+': '+r.content for r in reversed(rows)]
        channel=await route(self,content,history,state)
        if channel=='plain':
            full=''
            async for chunk in self.model.astream([HumanMessage(content='你是知行旅行助手，用简洁中文回答。\n'+'\n'.join(history))]):
                if isinstance(chunk.content,str) and chunk.content:
                    full+=chunk.content;await emit('assistant',chunk.content)
            return {'text':full,'streamed':True,'extra':{'route':'plain'}}
        confirmed=bool(re.fullmatch(r'(确认|确定|好的|可以|满意|ok|OK)[。！!\s]*',content.strip()))
        if confirmed and state.get('current_step')=='destination_recommendation':
            await self.write(cid,{'confirmed_revision':state.get('revision',0),'current_step':'transport_planning'})
            return await self.advance(cid,user_id,emit)
        agent=make_agent(self,user_id,await self.memory(user_id))
        result=await agent.ainvoke({'messages':[HumanMessage(content=content)],'user_id':user_id},
           {**self.config(cid),'recursion_limit':16},context={'confirmed':confirmed})
        for attempt in range(2):
            last=next((m for m in reversed(result['messages']) if isinstance(m,AIMessage)),None)
            if last is None or not last.invalid_tool_calls:break
            result=await agent.ainvoke({'messages':[]},{**self.config(cid),'recursion_limit':16},context={'confirmed':confirmed})
        last=next((m for m in reversed(result['messages']) if isinstance(m,AIMessage)),None)
        if last is not None and last.invalid_tool_calls:raise ValueError('模型工具参数连续无效，本轮未执行，请重试。')
        final=next((str(m.content) for m in reversed(result['messages']) if isinstance(m,AIMessage) and m.content and not m.tool_calls),'')
        after=await self.state(cid)
        if after.get('current_step') in ('transport_planning','accommodation_planning','food_planning','itinerary_generation'):
            return await self.advance(cid,user_id,emit)
        return {'text':final,'extra':{'metrics':metrics.summary() if hasattr(metrics,'summary') else {'model_calls':metrics.model_calls if hasattr(metrics,'model_calls') else None}}}
