import httpx,pytest
from quarry.api.app import app

@pytest.mark.asyncio
async def test_document_status_requires_key():
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test')as client:
            r=await client.get('/v1/documents/00000000-0000-0000-0000-000000000000')
    assert r.status_code==401

@pytest.mark.asyncio
async def test_unknown_route_uses_same_error_contract():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test')as client:
        r=await client.get('/not-a-route')
    assert r.status_code==404
    assert r.json()['error']['code']=='not_found'
