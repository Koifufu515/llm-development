import pytest
from app.full.domain import Requirement,budget
from app.full.selection_tools import match_transport,match_hotel,LegChoice,next_segment
from app.full.completion_tools import check_dependencies

def test_text_selection_wrong_leg_and_fake_price_are_not_applied():
 option={'name':'G123 二等座','train_code':'G123','seat_type':'二等座','availability':'有票','price_yuan':85,'option_id':'real'}
 segment={'from':'上海','to':'苏州','segment_id':'s1','options':[option]}
 with pytest.raises(ValueError):match_transport(segment,LegChoice(from_city='苏州',to_city='上海',vehicle_no='G123',seat_class='二等座'))
 picked=match_transport(segment,LegChoice(from_city='上海',to_city='苏州',vehicle_no='G123',seat_class='二等座',price=1))
 assert picked['price_yuan']==85

def test_hotel_city_guard_and_next_segment():
 segment={'segment_id':'h1','city':'苏州','options':[{'name':'如家（品牌参考）','mode':'brand','option_id':'a'}]}
 with pytest.raises(ValueError):match_hotel(segment,'杭州：如家')
 assert match_hotel(segment,'苏州：如家')['option_id']=='a'
 assert next_segment({'mode':'hotel','segments':[segment]},[])==segment

def test_dependency_guard_and_ticket_details():
 with pytest.raises(ValueError):check_dependencies({'requirement':{}},'itinerary_generation')
 req=Requirement(departure_city='苏州',destinations=['苏州'],departure_date='2026-11-01',travel_days=1,adult_count=3)
 out=budget(req,[],[],[{'name':'明确票价示例','price':20}],hotel_rooms=3)
 attraction=[i for i in out['items'] if i['category']=='attractions']
 assert attraction[0]['amount']==60 and attraction[0]['basis']=='estimate' and out['rooms']==3


def test_all_original_named_tools_and_rollback_aliases_registered():
    from types import SimpleNamespace
    from app.full.agent import build_tools
    service=SimpleNamespace(mcp_manager=SimpleNamespace(registered_tools=lambda:{}))
    tools=build_tools(service,'u')
    required={'record_requirement_tool','select_destination_tool','select_transport_tool','select_accommodation_tool','select_food_tool','select_accommodation_food_tool','generate_itinerary_tool','submit_itinerary_body_tool','summarize_budget_tool','go_back_to_budget','go_back_to_requirement'}
    assert required<=tools.keys()
    assert 'target' not in tools['go_back_to_budget'].tool_call_schema.model_json_schema().get('properties',{})

def test_flight_structural_fallback_does_not_treat_outage_as_no_airport():
    from app.full.capabilities import flight_needs_rail_fallback
    assert flight_needs_rail_fallback({'mode':'flight','segments':[{'status':'unsupported_city','options':[]}]})
    assert not flight_needs_rail_fallback({'mode':'flight','segments':[{'status':'unavailable','options':[]}]})
