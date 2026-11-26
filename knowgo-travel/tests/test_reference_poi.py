from types import SimpleNamespace
import pytest
from pydantic import SecretStr
from app.full.plans import poi_matches,enrich_map

def test_attraction_not_its_parking_or_other_branch():
    assert not poi_matches('苏州博物馆参观','苏州博物馆本馆地下停车场(内部专用)')
    assert not poi_matches('苏州博物馆参观','苏州博物馆西馆')
    assert poi_matches('苏州博物馆西馆参观','苏州博物馆西馆')
    assert poi_matches('苏州博物馆参观','苏州博物馆(本馆)')
    assert poi_matches('松鹤楼晚餐','松鹤楼餐厅')
    assert poi_matches('苏州博物馆本馆参观','苏州博物馆(本馆)')
    assert not poi_matches('拙政园深度游览','拙政园酒店',kind='attraction')

@pytest.mark.asyncio
async def test_map_chooses_main_attraction_before_auxiliary(monkeypatch):
    import app.full.plans as p
    monkeypatch.setattr(p,'Settings',lambda:SimpleNamespace(amap_api_key=SecretStr('')))
    class Remote:
        async def query(self,*args):
            return {'data':{'pois':[{'name':'苏州博物馆本馆地下停车场(内部专用)','location':'120.628,31.325'},{'name':'苏州博物馆(本馆)','location':'120.629,31.325'}]}}
    services=SimpleNamespace(remote=Remote(),mcp_manager=SimpleNamespace(tools={}))
    body={'days':[{'city':'苏州','day':1,'morning':[{'kind':'attraction','name':'苏州博物馆参观'}],'noon':[],'afternoon':[],'evening':[]}]}
    result=await enrich_map(services,body)
    assert [p['name']for p in result['points']]==['苏州博物馆(本馆)']

def test_activity_description_is_not_part_of_poi_name():
    from app.full.plans import poi_keyword
    for name,expected in [('观前街文化漫步与本地小吃初体验','观前街'),('平江路历史街区夜游','平江路'),('苏州博物馆本馆参观','苏州博物馆本馆'),('拙政园经典园林深度游览','拙政园'),('金鸡湖环湖骑行或亲水步道漫步','金鸡湖')]:
        assert poi_keyword(name)==expected
