import pytest
from pydantic import ValidationError
from app.full.domain import Requirement,budget,ItineraryBody,validate_body
from app.full.plans import citation_schema
from app.full.capabilities import auto_pick,validate_selection

def test_model_cannot_submit_an_invented_citation():
    model=citation_schema(['G1','G2'])
    schema=model.model_json_schema()
    assert schema['$defs']['CitedActivity']['properties']['source_ids']['items']['enum']==['G1','G2']
    activity={'name':'参观园林','kind':'attraction','description':'沿园林主要游览路线参观，注意台阶与步行安全。','start_time':'10:00','end_time':'11:00','source_ids':['虚构']}
    day={'day':1,'city':'苏州',**{s:[activity] for s in ('morning','noon','afternoon','evening')},'tips':['核对开放情况']}
    with pytest.raises(ValidationError):model.model_validate({'title':'苏州旅行','days':[day]})

def test_cross_midnight_arrival_blocks_sightseeing_before_arrival():
    req=Requirement(departure_city='上海',destinations=['北京'],departure_date='2026-10-31',travel_days=2)
    def act(start,end):return {'name':'参观景点','kind':'attraction','description':'按当地开放公告核实后参观，保留足够交通时间。','start_time':start,'end_time':end}
    body=ItineraryBody(title='北京旅行',days=[{'day':i,'city':'北京','morning':[act('09:00','10:00')],'noon':[act('12:00','13:00')],'afternoon':[act('14:00','15:00')],'evening':[act('18:00','19:00')],'tips':['核对预约']} for i in (1,2)])
    with pytest.raises(ValueError,match='到达'):
        validate_body(body,req,[{'from':'上海','to':'北京','date':'2026-10-31','departure_date':'2026-10-31','arrival_date':'2026-11-01','departure_time':'22:00','arrival_time':'08:00'}])

def test_no_ticket_segment_is_not_a_fake_required_selection():
    payload={'mode':'train','segments':[{'segment_id':'s1','options':[{'option_id':'x','availability':'无','price_yuan':20}]}]}
    assert validate_selection(payload,auto_pick(payload))==[]

def test_driving_budget_is_per_car_and_every_ledger_line_reconciles():
    req=Requirement(departure_city='上海',destinations=['苏州'],departure_date='2026-10-31',travel_days=1,adult_count=4,transport_types=['driving'])
    result=budget(req,[{'segment_id':'s1','mode':'driving','distance_km':100,'tolls_yuan':40}],[])
    first=result['items'][0]
    assert first['quantity']==1 and first['amount']==105
    assert all(round(r['quantity']*r['unit_price'],2)==r['amount'] for r in result['items'])


def test_map_must_not_replace_an_attraction_with_first_unrelated_search_hit():
    from app.full.plans import poi_matches,poi_keyword
    assert poi_keyword('拙政园游览')=='拙政园'
    assert poi_matches('苏州博物馆参观','苏州博物馆(本馆)')
    assert poi_matches('平江路历史文化街区漫步','平江路')
    assert not poi_matches('拙政园游览','寒山寺')
    assert not poi_matches('平江路历史文化街区漫步','石路步行街')


def test_mixed_transport_falls_back_to_available_mode_without_fake_tickets():
    data={'mode':'mixed','priority':['train','flight'],'segments':[{'segment_id':'s1','options':[{'mode':'train','option_id':'soldout','availability':'无','price_yuan':100},{'mode':'flight','option_id':'flight','price_yuan':None,'departure_time':'09:00','arrival_time':'11:00'}]}]}
    picks=validate_selection(data,auto_pick(data))
    assert len(picks)==1 and picks[0]['option_id']=='flight' and picks[0]['price_yuan'] is None


def test_train_without_quote_stays_unknown_but_can_be_selected():
    data={'mode':'train','segments':[{'segment_id':'s1','options':[{'option_id':'x','availability':'有','price_yuan':None,'duration':'01:00'}]}]}
    assert validate_selection(data,auto_pick(data))[0]['price_yuan'] is None

def test_direct_queries_report_known_zero_model_usage_and_no_fake_ttft():
    from app.core.telemetry import RequestMetrics
    r=RequestMetrics().snapshot()
    assert r['llm_calls']==0 and r['input_tokens']==0 and r['output_tokens']==0 and r['usage_complete']
    assert r['first_token_seconds'] is None


def test_invalid_tool_json_is_retained_in_checkpoint_but_not_resent_to_provider():
    from langchain_core.messages import AIMessage
    from app.full.agent import repair_history,RequirementPatch
    m=AIMessage(content='',invalid_tool_calls=[{'name':'record_requirement_tool','args':'{"updates":','id':'broken','error':'invalid json'}],additional_kwargs={'tool_calls':[{'id':'broken','type':'function','function':{'name':'record_requirement_tool','arguments':'{"updates":'}}]})
    fixed=repair_history([m])[0]
    assert m.invalid_tool_calls and not fixed.invalid_tool_calls and 'tool_calls' not in fixed.additional_kwargs
    patch=RequirementPatch(departure_city='上海',travel_days=2)
    assert patch.model_dump(exclude_unset=True)=={'departure_city':'上海','travel_days':2}
    assert RequirementPatch.model_json_schema()['additionalProperties'] is False
