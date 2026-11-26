"""原方案高德stdio MCP主天气源；主源失败独立降级，不用别日天气冒充目标日期。"""
import asyncio,json
from app.core.rail import content_text
from app.mcp_core.servers.weather_data import safely_query,query_weather

async def fetch_weather(services,city,day=None):
    primary=None
    try:
        tools=services.mcp_manager.tools.get('weather') or await services.mcp_manager.load_service('weather')
        tool=next(t for t in tools if t.name=='get_weather_forecast')
        primary=json.loads(content_text(await asyncio.wait_for(tool.ainvoke({'city':city,'date':day}),25)))
        if not primary.get('error') and primary.get('casts') and primary.get('status','ok')=='ok':
            return {**primary,'status':'ok','source':'高德天气','requested_date':day}
    except Exception as exc:primary={'status':'unavailable','reason':type(exc).__name__}
    try:
        tools=services.mcp_manager.tools.get('backup_weather') or await services.mcp_manager.load_service('backup_weather')
        tool=next(t for t in tools if 'weather' in t.name.lower())
        backup=json.loads(content_text(await asyncio.wait_for(tool.ainvoke({'city':city,'date':day}),25)))
    except Exception:backup=await safely_query(query_weather,city,day)
    return {**backup,'primary_status':primary.get('status',primary.get('error','unavailable')),'primary_recent_forecast':primary.get('casts',[]),'fallback':True}

def render_weather(city,data):
    if not data:return city+'天气暂不可用。'
    casts=data.get('casts',[]);forecast=data.get('forecast',[])
    if data.get('status')!='ok':return city+'：所选日期天气暂不可用，请在出行前核实；'+str(data.get('message') or data.get('error') or '数据源未返回有效预报。')
    lines=[f"**{city}天气**（来源：{data.get('source','天气服务')}）"]
    for c in casts:lines.append(f"- {c['date']}：白天{c.get('dayweather','未知')}，{c.get('nighttemp','未知')}～{c.get('daytemp','未知')}°C，{c.get('daywind','未知')}风{c.get('daypower','未知')}级")
    for c in forecast:lines.append(f"- {c['date']}：{c.get('weather_description','未知')}，{c.get('temperature_min_c','未知')}～{c.get('temperature_max_c','未知')}°C")
    return '\n'.join(lines)
