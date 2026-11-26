from app.full.capabilities import auto_pick

def hotel(price,score,name):return {'nightly_price_yuan':price,'rating':score,'option_id':name}
def pick(rows):return auto_pick({'mode':'hotel','segments':[{'segment_id':'h1','options':rows}]})[0]['option_id']
def test_hotel_prefers_qualified_rating_before_price():
    assert pick([hotel(100,4.2,'cheap-low'),hotel(200,4.6,'qualified'),hotel(250,4.9,'higher')])=='qualified'
def test_without_qualified_rating_uses_highest_then_cheapest():
    assert pick([hotel(100,3,'cheap'),hotel(200,4.3,'high'),hotel(160,4.3,'high-cheaper')])=='high-cheaper'

import pytest
from types import SimpleNamespace
from app.full.weather import fetch_weather,render_weather
class FakeTool:
    name='get_weather_forecast'
    async def ainvoke(self,args):return '{"status":"ok","source":"高德天气","casts":[{"date":"2026-10-31","dayweather":"小雨","daytemp":"20","nighttemp":"15","daywind":"东","daypower":"3"}]}'
@pytest.mark.asyncio
async def test_primary_weather_comes_from_registered_mcp_and_renders_exact_numbers():
    services=SimpleNamespace(mcp_manager=SimpleNamespace(tools={'weather':[FakeTool()]}))
    data=await fetch_weather(services,'苏州','2026-10-31')
    text=render_weather('苏州',data)
    assert data['source']=='高德天气' and '15～20°C' in text and '小雨' in text
