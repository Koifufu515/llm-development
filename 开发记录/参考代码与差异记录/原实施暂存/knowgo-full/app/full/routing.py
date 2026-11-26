"""事实直查在概率路由前；待补槽位保留查询种类，独立于规划状态。"""
import re,json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from langchain_core.messages import SystemMessage,HumanMessage
from pydantic import BaseModel,Field
from typing import Literal
from app.full.capabilities import CODES,transport_segment
from app.mcp_core.servers.weather_data import safely_query,query_weather

def parse_date(text):
    today=datetime.now(ZoneInfo('Asia/Shanghai')).date()
    match=re.search(r'(20\d{2})[-年/](\d{1,2})[-月/](\d{1,2})',text)
    if match:
        try:return today.replace(year=int(match[1]),month=int(match[2]),day=int(match[3])).isoformat()
        except ValueError:return None
    match=re.search(r'(\d{1,2})月(\d{1,2})',text)
    if match:
        try:return today.replace(month=int(match[1]),day=int(match[2])).isoformat()
        except ValueError:return None
    for token,days in [('大后天',3),('后天',2),('明天',1),('今天',0)]:
        if token in text:return (today+timedelta(days=days)).isoformat()
    return None

def cities_in(text):
    from pathlib import Path
    names=sorted(json.loads(Path(__file__).with_name('cities.json').read_text()),key=len,reverse=True)
    hits=[];occupied=[]
    for name in names:
        for m in re.finditer(re.escape(name),text):
            if any(a<m.end() and m.start()<b for a,b in occupied):continue
            occupied.append((m.start(),m.end()));hits.append((m.start(),name))
    return list(dict.fromkeys(name for _,name in sorted(hits)))

class Route(BaseModel):
    channel:Literal['planning','plain']=Field(description='planning=旅行行程安排、旅行需求补充、行程修改或相关追问；plain=问候、感谢、能力介绍、非规划闲聊。')

async def direct_query(services,cid,content,emit):
    namespace=('full_direct',cid);entry=await services.store.aget(namespace,'pending')
    pending=entry.value if entry else None
    if pending and datetime.fromisoformat(pending['created_at'])<datetime.now(ZoneInfo('Asia/Shanghai'))-timedelta(minutes=10):pending=None
    planning=any(w in content for w in ('规划','行程','旅游','旅行','玩几天','预算','换目的地'))
    if planning:
        if entry:await services.store.adelete(namespace,'pending')
        return None
    kind='web' if any(w in content for w in ('景点','景区','开放时间','几点开门','门票','预约规则')) else 'weather' if '天气' in content else 'flight' if any(w in content for w in ('航班','机票')) else 'train' if any(w in content for w in ('高铁','车票','车次','火车')) else None
    if kind and pending and kind!=pending['kind']:pending=None
    query=any(w in content for w in ('查','有没有','哪些','明天','后天','今天','几号','天气')) or bool(parse_date(content)) or kind=='web'
    if not pending and not(kind and query):return None
    slot=pending or {'kind':kind,'created_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'turns':0}
    cities=cities_in(content);day=parse_date(content)
    if day:slot['date']=day
    if slot['kind']=='web':
        from app.full.websearch import search_web
        result=await search_web(services,cities[0] if cities else '',content)
        text='\n\n'.join(f"{r['title']}：{r['text']}\n来源：{r['source_url']}" for r in result['results']) or '本次联网检索未返回可靠摘要，请稍后重试。'
        await services.store.adelete(namespace,'pending')
        return {'text':text+'\n\n'+result['notice'],'extra':{'route':'direct','facts':result}}
    if slot['kind']=='weather':
        if cities:slot['city']=cities[0]
        missing=[] if slot.get('city') else ['城市']
    else:
        if len(cities)>=2:slot.update({'from':cities[0],'to':cities[1]})
        elif len(cities)==1:
            if not slot.get('from'):slot['from']=cities[0]
            elif not slot.get('to'):slot['to']=cities[0]
        missing=[label for key,label in [('from','出发城市'),('to','到达城市'),('date','日期')] if not slot.get(key)]
    if missing:
        slot['turns']+=1
        if slot['turns']<=3:await services.store.aput(namespace,'pending',slot)
        else:await services.store.adelete(namespace,'pending')
        return {'text':'请补充'+ '、'.join(missing)+'，我会查询实际数据。','extra':{'route':'direct','pending':True}}
    await services.store.adelete(namespace,'pending')
    if slot['kind']=='weather':
        result=await safely_query(query_weather,slot['city'],slot.get('date'))
        return {'text':slot['city']+'天气查询结果：\n'+__import__('json').dumps(result,ensure_ascii=False,indent=2),'extra':{'route':'direct','facts':result}}
    leg={'segment_id':'direct','from':slot['from'],'to':slot['to'],'date':slot['date']}
    result=await transport_segment(services,slot['kind'],leg)
    lines=[f"{slot['date']} {slot['from']} → {slot['to']}",'| 候选 | 出发 | 到达 | 参考价 | 余票 |','|---|---|---|---|---|']
    for row in result.get('options',[]):lines.append(f"| {row['name']} | {row.get('departure_time','')} | {row.get('arrival_time','')} | {row['price_yuan'] if row.get('price_yuan') is not None else '待定'} | {row.get('availability','未提供')} |")
    if not result.get('options'):lines.append(result.get('message','本次没有查到候选，不能据此认定该路线没有班次。'))
    lines.append('来源：'+str(result.get('source',slot['kind']))+'；余票与报价随时变化，尚未预订。')
    return {'text':'\n'.join(lines),'extra':{'route':'direct','facts':result}}

async def route(services,content,history,state):
    if any(w in content for w in ('记住','我的偏好','过敏','禁忌','规划','行程','旅游','旅行','出游')):return 'planning'
    if re.search(r'(去|玩|游).*(?:[一二三四五六七八九十两0-9]+[天日]|周末)',content):return 'planning'
    if len(cities_in(content))>=2 and any(w in content for w in ('安排','出发','去','待')):return 'planning'
    if content.strip().rstrip('。！!') in cities_in(content) and any(any(w in h for w in ('目的地','哪个城市','去哪')) for h in history[-2:]):return 'planning'
    if state.get('current_step') and (any(w in content for w in ('改成','换成','重新规划','调整','取消行程')) or re.fullmatch(r'(确认|确定|好的|可以|满意|ok)[。！!\s]*',content.strip(),re.I)):return 'planning'
    result=await services.model.with_structured_output(Route).ainvoke([
      SystemMessage(content='明确分类：创建或安排旅游行程、补充旅行需求、修改或追问已有旅行计划，选择planning。问候、感谢、能力介绍和非旅行规划闲聊选择plain。必须结合history与step；历史正在问城市/人数/预算时，短回答属于planning，不能脱离上下文按闲聊处理。'),
      HumanMessage(content=__import__('json').dumps({'history':history,'message':content,'step':state.get('current_step'),'requirement':state.get('requirement',{})},ensure_ascii=False))])
    return result.channel
