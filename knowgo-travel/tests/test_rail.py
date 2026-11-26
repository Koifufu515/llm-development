import json
from datetime import date, timedelta, datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from app.core.rail import normalize_query, compact_tickets, render_ticket_table
from app.mcp_core.client import ProjectMCPManager
from app.tools.rail_tools import make_rail_tool


def row(n=1):
    return {'start_train_code':f'G{n}', 'start_date':'2026-10-27','arrive_date':'2026-10-27',
            'start_time':f'{6+n//60:02}:{n%60:02}', 'arrive_time':'08:00','lishi':'00:30',
            'from_station':'上海虹桥','to_station':'苏州北','from_station_telecode':'AOH','to_station_telecode':'OHH',
            'prices':[{'seat_name':'二等座','num':'有','price':0}]}


QUERY={'date':'2026-10-27','fromStation':'上海','toStation':'苏州'}
REQ={'departure_date':'2026-10-27','departure_city':'上海','destination':'苏州'}


def test_aliases_are_removed_and_confirmed_route_wins():
    assert normalize_query({'trainDate':'2026-10-28','fromCity':'北京','toCity':'天津'},REQ,date(2026,10,26))==QUERY


@pytest.mark.parametrize('parameters,requirement,message',[
    ({},{},'缺少'),
    ({},{**REQ,'departure_date':'2026-10-25'},'已过去'),
    ({},{**REQ,'departure_date':'2026-11-20'},'查询窗口'),
    ({},{**REQ,'destination':'上海'},'本地游'),
])
def test_invalid_queries_do_not_get_automatic_date_replacement(parameters,requirement,message):
    with pytest.raises(ValueError,match=message):normalize_query(parameters,requirement,date(2026,10,26))


def test_large_result_is_sorted_and_limited_without_fake_facts():
    rows=[row(n) for n in reversed(range(1,101))]
    result=compact_tickets(json.dumps(rows),QUERY)
    assert result['original_count']==100 and result['shown_count']==12
    assert result['options'][0]['train_code']=='G1'
    assert result['options'][0]['seats'][0]['price_yuan']==0
    assert len(json.dumps(result))<result['original_characters']
    assert '上海虹桥' in render_ticket_table(result)


def test_empty_is_different_from_failed_or_malformed():
    assert compact_tickets('[]',QUERY)['status']=='empty'
    with pytest.raises(ValueError):compact_tickets('Error: network failed',QUERY)


def test_wrong_date_in_upstream_data_is_not_displayed():
    item=row();item['start_date']='2026-10-26'
    with pytest.raises(ValueError,match='日期'):compact_tickets(json.dumps([item]),QUERY)


def test_option_id_distinguishes_same_train_at_different_stations():
    a=row();b={**a,'to_station':'张家港','to_station_telecode':'ZAU'}
    result=compact_tickets(json.dumps([a,b]),QUERY)
    assert result['options'][0]['option_id']!=result['options'][1]['option_id']


@pytest.mark.asyncio
async def test_invalid_date_does_not_call_external_service():
    class Manager:
        tools={}
        async def load_service(self,name):raise AssertionError('不应联网')
    tool=make_rail_tool(Manager())
    runtime=SimpleNamespace(state={'current_step':'transport_planning','requirement_confirmed':True,'user_requirement':{**REQ,'departure_date':'2099-01-01'}},tool_call_id='test')
    result=await tool.coroutine(runtime=runtime)
    assert result.update['last_transport_query']['code']=='invalid_query'
    assert result.update['transport_options']==[]


@pytest.mark.asyncio
async def test_service_failure_does_not_cancel_other_service(monkeypatch):
    import app.mcp_core.client as client_module
    async def healthy_weather():return ['weather-tool']
    class FailedRailClient:
        def __init__(self,*args,**kwargs):pass
        async def get_tools(self):raise ConnectionError('injected rail failure')
    monkeypatch.setattr(client_module,'load_weather_tools',healthy_weather)
    monkeypatch.setattr(client_module,'MultiServerMCPClient',FailedRailClient)
    manager=ProjectMCPManager()
    await manager.initialize()
    assert manager.tools['weather']==['weather-tool']
    assert manager.status['weather']=='ready'
    assert manager.status['rail']=='unavailable'
