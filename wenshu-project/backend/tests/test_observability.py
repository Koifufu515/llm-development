import pytest
from app.utils.telemetry import TraceMiddleware,HTTP_REQUESTS

@pytest.mark.asyncio
async def test_unhandled_failure_is_counted_as_500():
 async def broken(scope,receive,send):raise RuntimeError('fixture failure')
 middleware=TraceMiddleware(broken)
 counter=HTTP_REQUESTS.labels('GET','unmatched','500');before=counter._value.get()
 async def receive():return {'type':'http.request','body':b''}
 async def send(message):pass
 with pytest.raises(RuntimeError):await middleware({'type':'http','method':'GET','headers':[]},receive,send)
 assert counter._value.get()==before+1

@pytest.mark.asyncio
async def test_memory_prompt_budget_with_large_entities_terminates(fresh_container):
 from app.memory.context_builder import MemoryContext
 c=fresh_container
 context=MemoryContext(session={'summary':'摘要'*6000,'entities':{'matter':'事项'*6000},'recent_messages':[]})
 c.memory_context_builder._apply_budget(context)
 assert len(context.prompt_text())<=c.settings.memory_context_max_chars
