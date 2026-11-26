from copy import deepcopy
import pytest
from pydantic import ValidationError
from app.full.reference_itinerary import _normalize_itinerary_days,ItineraryBody,normalize_enhanced_body
from app.full.domain import Requirement,ItineraryBody as Enhanced,validate_body

def long():return '参观前在官方渠道核实开放公告与预约要求，根据当天实际交通和天气灵活调整游玩节奏，不承诺门票报价，不安排缺少依据的具体线路，并为进出场馆和市内交通预留余量。'

def test_reference_repairs_missing_day_slots_city_return():
 raw=[{'day':1,'morning':[long()],'noon':[],'afternoon':[],'evening':[],'tips':[]}]
 before=deepcopy(raw)
 fixed,log=_normalize_itinerary_days(raw,2,cities=['苏州','杭州'])
 ItineraryBody.model_validate({'days':fixed},context={'travel_days':2})
 assert len(fixed)==2 and fixed[0]['morning']==raw[0]['morning']
 assert fixed[1]['city']=='杭州' and any('返程' in t for t in fixed[1]['evening'])
 assert raw==before and log

def test_reference_drops_duplicate_and_out_of_range():
 fixed,log=_normalize_itinerary_days([{'day':2},{'day':2},{'day':0},{'day':9}],2,cities=['苏州']*2)
 assert [d['day'] for d in fixed]==[1,2] and sum('忽略' in t for t in log)==3

@pytest.mark.parametrize('broken', ['short','gap','no_return'])
def test_original_validation_rejects_noncompliant_body(broken):
 days,_=_normalize_itinerary_days([],2,cities=['苏州']*2)
 if broken=='short':days[0]['tips']=['短句']
 elif broken=='gap':days=days[1:]
 else:days[-1]['evening']=[long()]
 with pytest.raises(ValidationError):ItineraryBody.model_validate({'days':days},context={'travel_days':2})

def test_enhanced_adapter_preserves_valid_activity_and_alias():
 req=Requirement(departure_city='上海',destinations=['苏州'],departure_date='2026-11-01',travel_days=1)
 activity={'name':'苏州博物馆','kind':'attraction','description':long(),'start_time':'09:00','end_time':'11:00','source_ids':['G1']}
 raw={'title':'苏州一日游','days':[{'day':1,'city':'苏州','morning':[activity]}]}
 enhanced,reference,fixes=normalize_enhanced_body(raw,req,[])
 validate_body(Enhanced.model_validate(enhanced),req,[])
 assert enhanced['days'][0]['morning'][0]==activity and fixes
 assert reference['days'][0]['morning']==[long()]
