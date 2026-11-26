import httpx
import pytest

from app.mcp_core.servers.weather_data import query_weather, safely_query, resolve_city


@pytest.fixture
def client():
    def handle(request):
        if 'geocoding-api' in request.url.host:
            return httpx.Response(200, json={"results": [{"name":"杭州", "admin1":"浙江", "latitude":30.2,"longitude":120.1,"timezone":"Asia/Shanghai"}]})
        return httpx.Response(200, json={"daily":{"time":["2026-10-24","2026-10-25"],"weather_code":[0,61],"temperature_2m_max":[23,21],"temperature_2m_min":[15,14],"precipitation_probability_max":[0,80]}})
    return httpx.AsyncClient(transport=httpx.MockTransport(handle))


@pytest.mark.asyncio
async def test_specific_date_returns_only_requested_day(client):
    async with client:
        result=await query_weather(client,"杭州","2026-10-25")
    assert result['status']=='ok'
    assert len(result['forecast'])==1
    assert result['forecast'][0]['date']=='2026-10-25'
    assert result['forecast'][0]['rain_probability_percent']==80
    assert result['forecast'][0]['weather_description']=='小雨'
    assert result['source'] and result['queried_at']


@pytest.mark.asyncio
async def test_out_of_range_does_not_return_other_dates(client):
    async with client:
        result=await query_weather(client,"杭州","2099-01-01")
    assert result['code']=='date_out_of_range'
    assert 'forecast' not in result
    assert result['available_window']['end']=='2026-10-25'


@pytest.mark.asyncio
async def test_invalid_date_does_not_query_network(client):
    async with client:
        result=await query_weather(client,"杭州","2026-02-30")
    assert result['code']=='invalid_date'


@pytest.mark.asyncio
async def test_unknown_city_has_clear_failure():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,json={'results':[]}))) as client:
        result=await query_weather(client,'不存在的测试城市')
    assert result['code']=='city_not_found'
    assert 'forecast' not in result


@pytest.mark.asyncio
async def test_ambiguous_city_returns_candidates():
    data={'results':[{'name':'测试城','admin1':'甲省'},{'name':'测试城','admin1':'乙省'}]}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,json=data))) as client:
        result=await resolve_city(client,'测试城')
    assert result['code']=='ambiguous_city' and len(result['candidates'])==2


@pytest.mark.asyncio
async def test_timeout_becomes_structured_failure():
    async def timeout(client,*args):
        raise httpx.ReadTimeout('test')
    result=await safely_query(timeout,'杭州')
    assert result['code']=='upstream_timeout'
    assert 'forecast' not in result


def test_weather_only_exposed_after_requirement_confirmation():
    from app.core.middleware import allowed_tool_names
    assert 'get_weather_forecast' not in allowed_tool_names({},None)
    assert 'get_weather_forecast' in allowed_tool_names({'requirement_confirmed':True,'current_step':'transport_planning'},None)
