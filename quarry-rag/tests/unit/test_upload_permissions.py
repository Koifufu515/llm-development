import httpx,pytest
from quarry.api.app import app
from quarry.api.security import Caller,require_caller

@pytest.mark.asyncio
async def test_upstream_search_key_cannot_write_corpus():
 app.dependency_overrides[require_caller]=lambda:Caller('test','knowgo-travel',['public'],['travel-guide'],60)
 try:
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test')as c:
   r=await c.post('/v1/documents',params={'collection_slug':'travel-guide'},files={'file':('a.md',b'fixture')})
  assert r.status_code==403
 finally:app.dependency_overrides.clear()
