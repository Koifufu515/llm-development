import asyncio
from datetime import date,timedelta
import pytest
from langchain_core.tools import StructuredTool
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph,MessagesState,START,END
from app.full.rail_guard import _guard_train_tool,set_turn_context

@pytest.mark.asyncio
async def test_actual_toolnode_uses_guard_and_task_context_does_not_cross_sessions():
 captured=[]
 async def raw(**kwargs):
  captured.append(kwargs)
  return '\n'.join(f'G{i+100} 上海(telecode:SHH) -> 苏州(telecode:SZH) 08:{i:02d} -> 09:{i:02d} 历时：01:00\n- 二等座: 有票 30元' for i in range(20))
 schema={'type':'object','properties':{k:{'type':'string'} for k in ('date','fromStation','toStation')},'required':['date','fromStation','toStation']}
 original=StructuredTool(name='get-tickets',description='spy',args_schema=schema,coroutine=raw)
 guarded=_guard_train_tool(original);node=ToolNode([guarded]);builder=StateGraph(MessagesState);builder.add_node('tools',node);builder.add_edge(START,'tools');builder.add_edge('tools',END);graph=builder.compile();day=(date.today()+timedelta(days=2)).isoformat()
 async def one(frm,to):
  set_turn_context(frm,to,day,True,frm,to)
  return await graph.ainvoke({'messages':[AIMessage(content='',tool_calls=[{'name':'get-tickets','args':{'trainDate':'2099-01-01'},'id':frm}])]},config={'configurable':{'thread_id':frm}})
 results=await asyncio.gather(one('上海','苏州'),one('北京','天津'))
 assert {(r['fromStation'],r['toStation']) for r in captured}=={('上海','苏州'),('北京','天津')}
 assert all(r['date']==day and 'trainDate' not in r for r in captured)
 assert all('仅列前 12 趟' in r['messages'][-1].content for r in results)
