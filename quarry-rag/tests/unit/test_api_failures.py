import asyncio
from types import SimpleNamespace
import httpx,pytest
from quarry.api.app import app
from quarry.api.security import Caller,require_caller
from quarry.api import routes

@pytest.mark.asyncio
async def test_total_timeout_has_structured_504_and_a_log(monkeypatch):
 calls=[]
 async def slow(*a,**kw):await asyncio.sleep(.05)
 async def log(**kw):calls.append(kw)
 monkeypatch.setattr(routes,'search_evidence',slow);monkeypatch.setattr(routes,'log_query',log)
 monkeypatch.setattr(routes,'get_settings',lambda:SimpleNamespace(default_top_k=8,api_max_top_k=20,api_request_timeout_s=.005))
 app.dependency_overrides[require_caller]=lambda:Caller('k','test',['public'],['travel-guide'],60)
 try:
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test')as c:r=await c.post('/v1/search',json={'collection':'travel-guide','query':'test'})
  assert r.status_code==504 and r.json()['error']['code']=='timeout'
  assert calls[0]['status']==504 and calls[0]['request_id']==r.headers['X-Request-Id']
 finally:app.dependency_overrides.clear()
