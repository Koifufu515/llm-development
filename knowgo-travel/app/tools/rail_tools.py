import asyncio
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from app.core.rail import normalize_query, compact_tickets
from app.core.state import TravelState
from app.core.transitions import ConfirmationContext


def make_rail_tool(manager):
    @tool
    async def query_train_tickets(parameters: dict[str, str] | None = None, runtime: ToolRuntime[ConfirmationContext, TravelState] = None) -> Command:
        """查询已确认行程的高铁/动车去程余票。参数可省略，读取当前出发城市、目的地和日期。

        parameters支持date/fromStation/toStation及trainDate/fromCity/toCity别名，但已确认的行程字段优先。
        用户要改日期或路线，应先记录需求并重新确认。本工具只查票，不选票，不推进。
        """
        state=runtime.state
        stamp=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
        if not state.get('requirement_confirmed') or state.get('current_step')!='transport_planning':
            result={'status':'unavailable','code':'unconfirmed','message':'请先补齐并确认需求'}
        else:
            try:
                query=normalize_query(parameters or {},state.get('user_requirement',{}),datetime.now(ZoneInfo('Asia/Shanghai')).date())
            except ValueError as exc:
                result={'status':'unavailable','code':'invalid_query','message':str(exc)}
            else:
                try:
                    tools=manager.tools.get('rail',[])
                    if not tools:tools=await manager.load_service('rail')
                    ticket=next((t for t in tools if t.name=='get-tickets'),None)
                    if ticket is None:raise RuntimeError('rail service unavailable')
                    content=await asyncio.wait_for(ticket.ainvoke({**query,'trainFilterFlags':'GD','format':'json','sortFlag':'startTime','limitedNum':0}),timeout=45)
                    result=compact_tickets(content,query)
                except (ValueError,KeyError,TypeError):
                    result={'status':'unavailable','code':'invalid_upstream_result','message':'车票数据源返回失败或格式异常，本次没有得到可验证结果，请稍后重试。'}
                except Exception:
                    manager.tools['rail']=[]
                    manager.status['rail']='unavailable'
                    result={'status':'unavailable','code':'rail_unavailable','message':'车票服务暂时不可用，请稍后重试；天气查询仍可单独使用。'}
        result['queried_at']=stamp
        update={'last_transport_query':result, 'transport_options':result.get('options',[]),
                'messages':[ToolMessage(content=json.dumps(result,ensure_ascii=False),name='query_train_tickets',tool_call_id=runtime.tool_call_id)]}
        return Command(update=update)
    return query_train_tickets
