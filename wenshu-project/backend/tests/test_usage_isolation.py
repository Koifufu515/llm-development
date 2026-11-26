import asyncio
import pytest
from app.llm.usage import request_usage,record

@pytest.mark.asyncio
async def test_usage_isolated_across_concurrent_requests():
 @request_usage
 async def request(name):
  record('completion',name,{'prompt_tokens':1,'completion_tokens':2})
  await asyncio.sleep(0)
  return {}
 a,b=await asyncio.gather(request('a'),request('b'))
 assert [c['model']for c in a['model_usage']['calls']]==['a']
 assert [c['model']for c in b['model_usage']['calls']]==['b']
 assert a['model_usage']['cost_yuan']is None
