import pytest
from app.full.intents import detect_intent
from app.full.transport_switch import detect_transport_switch
from app.full.domain import Requirement,topology

@pytest.mark.parametrize('text', ['明天苏州多少度','明天上海带伞吗','杭州冷不冷'])
def test_original_colloquial_weather(text):assert detect_intent(text).weather_object

def test_planning_not_stolen_by_train_direct():
 i=detect_intent('明天坐高铁去杭州旅游');assert i.planning_noise and not i.looks_like_query

@pytest.mark.parametrize('text,expected', [('不要飞机，改坐高铁','train'),('高铁没票，还是开车吧','driving'),('高铁吧','train'),('不要高铁了',None),('航班太贵，不坐飞机了',None),('我已按卡片选择高铁',None)])
def test_original_switch_negation(text,expected):assert detect_transport_switch(text,'flight')==expected

def test_reference_city_order_explicit_days_are_city_bound():
 r=Requirement(departure_city='上海',destinations=['苏州','上海'],departure_date='2026-11-01',travel_days=5,city_days=[3,2])
 t=topology(r);assert t['cities']==['上海','苏州']
 assert [d['city'] for d in t['days']]==['上海','上海','苏州','苏州','苏州']
 assert [s['nights'] for s in t['stays']]==[2,2]
