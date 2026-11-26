import pytest
from langgraph.graph import StateGraph,START,END
from app.full.agent import FullState,CLEAR,reset_after,repair_history
from app.full.capabilities import validate_selection,flight_prices
from langchain_core.messages import AIMessage,HumanMessage,ToolMessage

def test_real_reducer_clears_products():
    graph=StateGraph(FullState)
    graph.add_node('produce',lambda s:{'itinerary_body':{'days':[1]},'budget':{'total':3000}})
    graph.add_node('rollback',lambda s:reset_after('accommodation_planning'))
    graph.add_edge(START,'produce');graph.add_edge('produce','rollback');graph.add_edge('rollback',END)
    result=graph.compile().invoke({'messages':[]})
    assert result['itinerary_body'] is None and result['budget'] is None

def test_duplicate_and_unsold_selection_are_rejected():
    payload={'mode':'train','segments':[{'segment_id':'s1','options':[{'option_id':'a','availability':'有票'}]}]}
    with pytest.raises(ValueError,match='重复'):validate_selection(payload,[{'segment_id':'s1','option_id':'a'}]*2)
    payload['segments'][0]['options'][0]['availability']='候补'
    with pytest.raises(ValueError,match='现票'):validate_selection(payload,[{'segment_id':'s1','option_id':'a'}])

def test_fare_is_matched_to_flight_not_route_minimum():
    assert flight_prices({'lowestPrice':100,'data':[{'flightNo':'CA1234','price':500},{'flightNo':'CA1234','price':450},{'flightNo':'MU1234','fuel':100}]})=={'CA1234':450}

def test_repair_drops_orphan_and_fills_dangling():
    rows=[AIMessage(content='',tool_calls=[{'id':'t1','name':'query','args':{}}]),ToolMessage(content='bad',tool_call_id='unknown'),HumanMessage(content='继续')]
    result=repair_history(rows)
    assert [m.tool_call_id for m in result if isinstance(m,ToolMessage)]==['t1']


def test_actual_variflight_lowercase_cabins():
    data={'data':[{'flightno':'CA1518','cabins':[{'cabinclass':'C','price':2800},{'cabinclass':'Y','price':910}]}]}
    assert flight_prices(data)=={'CA1518':910}
