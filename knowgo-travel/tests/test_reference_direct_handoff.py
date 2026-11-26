import pytest
from types import SimpleNamespace
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage,HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from app.full.agent import make_agent
from app.core.telemetry import RequestMetrics
class BoundFake(FakeMessagesListChatModel):
 def bind_tools(self,tools,**kwargs):return self
@pytest.mark.asyncio
async def test_one_confirmation_does_not_start_another_model_round():
 model=BoundFake(responses=[AIMessage(content='',tool_calls=[{'name':'select_food_tool','args':{'food_preferences':['local']},'id':'f'}])])
 s=SimpleNamespace(model=model,mcp_manager=SimpleNamespace(registered_tools=lambda:{}),checkpointer=InMemorySaver(),store=InMemoryStore())
 graph=make_agent(s,'u',{});metrics=RequestMetrics()
 result=await graph.ainvoke({'messages':[HumanMessage(content='餐饮选本地小吃')],'current_step':'food_planning','revision':1,'requirement':{}},config={'configurable':{'thread_id':'direct'},'callbacks':[metrics]})
 assert result['food_preferences']==['local'] and result['current_step']=='itinerary_generation'
 assert metrics.calls==1
