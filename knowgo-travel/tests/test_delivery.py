import asyncio
from datetime import date
from uuid import uuid4
import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from app.services.contracts import PlanRequest
from app.services.planning import budget_for,choose_train,generate_validated
from app.services.providers import collect_queries
from app.core.telemetry import RequestMetrics
from app.services.routing import classify
from app.core.store import open_store,update_preferences
from app.config import Settings


def req(**updates):
    return PlanRequest(session_id=uuid4(),departure_city='上海',departure_date=date(2026,11,1),
        stops=[{'city':'苏州','days':3}],budget_per_person=2000,**updates)


def test_multicity_date_offsets_and_zero_leg():
    r=req().model_copy(update={'stops':req().stops})
    assert r.legs()[0]['date']=='2026-11-01'
    assert req().model_copy(update={'departure_city':'苏州'}).legs()==[]


def test_budget_unknown_is_not_zero_price_and_children_explicit():
    b=budget_for(req(children=1),[None])
    assert b['unpriced_transport_legs']==1 and not b['complete']
    assert b['hotel_estimate_total']==600 and b['food_estimate_total']==600
    assert '儿童' in ''.join(b['exclusions'])


def test_sold_out_not_auto_selected():
    assert choose_train({'options':[{'seats':[{'availability':'无','price_yuan':30}]}]}) is None

@pytest.mark.asyncio
async def test_parallel_failure_does_not_cancel_other_leg():
    async def ok():return {'status':'ok'}
    async def bad():raise RuntimeError('failure')
    result=await collect_queries([('one',ok),('two',bad)])
    assert result['one']['status']=='ok' and result['two']['status']=='unavailable'

@pytest.mark.asyncio
async def test_generation_retries_wrong_day_count_then_validates():
    model=FakeMessagesListChatModel(responses=[AIMessage(content='{"summary":"x","days":[]}'),AIMessage(content='{"summary":"x","days":[{"day":1,"city":"苏州","morning":"园林","afternoon":"漫步","evening":"休息"}]}')])
    one=req().model_copy(update={'stops':[req().stops[0].model_copy(update={'days':1})]})
    result=await generate_validated(model,one,{}, {},[],RequestMetrics())
    assert len(result['days'])==1

@pytest.mark.asyncio
async def test_two_invalid_generations_never_report_success():
    model=FakeMessagesListChatModel(responses=[AIMessage(content='not json')])
    with pytest.raises(ValueError,match='两次'):
        await generate_validated(model,req(),{}, {},[],RequestMetrics())

@pytest.mark.asyncio
async def test_real_store_overwrite_and_cross_session_restore():
    uid=str(uuid4());namespace=('users',uid,'preferences')
    async with open_store(Settings()) as store:
        await update_preferences(store,uid,{'pace':'轻松','hotel_type':'经济'})
        await update_preferences(store,uid,{'pace':'紧凑'})
    async with open_store(Settings()) as store:
        item=await store.aget(namespace,'profile')
        assert item.value=={'pace':'紧凑','hotel_type':'经济'}
        assert await store.aget(('users',str(uuid4()),'preferences'),'profile') is None
        await store.adelete(namespace,'profile')

@pytest.mark.asyncio
async def test_invalid_route_is_rejected():
    model=FakeMessagesListChatModel(responses=[AIMessage(content='{"channel":"invalid","intent":"rail"}')])
    with pytest.raises(ValueError):await classify(model,'测试',RequestMetrics(),'2026-10-29')


def test_real_hotel_prices_replace_only_priced_nights():
    b=budget_for(req(),[],[{'stay_total_yuan':400,'nights':2}])
    assert b['hotel_reference_total']==400
    assert b['hotel_estimate_total']==0
    assert b['known_and_estimated_total']==700


def test_multicity_change_can_force_revision_invalidation():
    from app.core.transitions import requirement_update
    from app.core.state import RequirementPatch
    state={'user_requirement':{'destination':'苏州'},'requirement_revision':4,'requirement_confirmed':True}
    result=requirement_update(state,RequirementPatch(destination='苏州'),force=True)
    assert result['requirement_revision']==5 and not result['requirement_confirmed']

@pytest.mark.asyncio
async def test_remote_prefix_python_literal_is_parsed_without_eval():
    from app.services.remote import RemoteProviders
    class Tool:
        name='searchFlightsByDepArr'
        async def ainvoke(self,args):return [{'type':'text','text':"Flight search results: {'data': [{'FlightNo': 'MU1'}]}"}]
    class Remote(RemoteProviders):
        async def discover(self,name):return [Tool()]
    result=await Remote().query('flight',('searchflights',),{})
    assert result['status']=='ok' and result['data']['data'][0]['FlightNo']=='MU1'

@pytest.mark.asyncio
async def test_waiting_selection_never_invokes_generation(monkeypatch):
    from app.services import planning
    class KB:
        def search(self,*args):return {'results':[]}
    async def fake_collect(*args,**kwargs):return {'rail:leg-0':{'status':'empty','options':[]}}
    monkeypatch.setattr(planning,'collect_queries',fake_collect)
    async def emit(*args):pass
    result=await planning.execute_plan(req(),None,None,KB(),{},RequestMetrics(),emit)
    assert result['status']=='waiting_selection' and not result['selected_hotels']
