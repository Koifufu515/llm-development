from types import SimpleNamespace
import pytest
from langchain_core.messages import HumanMessage,ToolMessage
from app.core.middleware import StepConfigMiddleware

@pytest.mark.asyncio
@pytest.mark.parametrize('saved',[False,True])
async def test_explicit_memory_calls_tool_once(saved):
    class Request:
        tool_choice=None
        system_message=None
        tools=[SimpleNamespace(name='remember_preferences')]
        runtime=SimpleNamespace(context=None)
        state={'messages':[HumanMessage(content='请长期记住我的饮食偏好：不吃辣')]}
        def override(self,**kwargs):return kwargs
    request=Request()
    if saved:request.state={'messages':[*request.state['messages'],ToolMessage(content='已保存',name='remember_preferences',tool_call_id='x')]}
    async def handler(value):return value
    result=await StepConfigMiddleware().awrap_model_call(request,handler)
    if saved:assert result['tool_choice'] is None
    else:assert result['tool_choice']['function']['name']=='remember_preferences'
