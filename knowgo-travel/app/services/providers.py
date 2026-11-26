"""外部数据只在成功返回时标为事实。缺少商业凭证显式声明。"""
import asyncio
from datetime import date, datetime
from zoneinfo import ZoneInfo
from app.core.rail import normalize_query, compact_tickets
from app.mcp_core.servers.weather_data import query_weather, safely_query

async def query_rail(manager, leg):
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    try:
        query=normalize_query({}, {"departure_city":leg['fromStation'],"destination":leg['toStation'],"departure_date":leg['date']},datetime.now(ZoneInfo('Asia/Shanghai')).date())
        tools=manager.tools.get('rail') or await manager.load_service('rail')
        tool=next(t for t in tools if t.name=='get-tickets')
        result=compact_tickets(await asyncio.wait_for(tool.ainvoke({**query,'trainFilterFlags':'GD','format':'json','sortFlag':'startTime','limitedNum':0}),45),query)
    except ValueError as exc:result={'status':'unavailable','code':'invalid_query','message':str(exc),'options':[]}
    except Exception:result={'status':'unavailable','code':'upstream_error','message':'实时交通查询失败，请稍后重试','options':[]}
    return {**result,'leg_id':leg['leg_id'],'requested':leg,'queried_at':stamp}

async def collect_queries(functions, parallel=True):
    async def guarded(name,fn):
        try:return name,await asyncio.wait_for(fn(),55)
        except Exception:return name,{'status':'unavailable','message':'查询失败或超时'}
    if parallel:
        rows=await asyncio.gather(*(guarded(name,fn) for name,fn in functions))
    else:
        rows=[await guarded(name,fn) for name,fn in functions]
    return dict(rows)

def lodging_status(city):
    return {'status':'unavailable','city':city,'source':None,'options':[],
        'message':'未配置实时酒店供应商；住宿预算使用用户填写的每晚估算，不代表可订房价。'}
