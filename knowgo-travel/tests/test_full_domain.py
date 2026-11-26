from app.full.domain import Requirement,topology,budget

def req(**kw):
    return Requirement(departure_city='上海',destinations=['杭州','南京'],departure_date='2026-11-01',travel_days=5,**kw)

def test_round_trip_windows_weighted_budget():
    r=req();t=topology(r)
    assert [x['day'] for x in t['days']]==[1,2,3,4,5]
    assert [(x['from'],x['to'],x['date']) for x in t['legs']]==[('上海','杭州','2026-11-01'),('杭州','南京','2026-11-02'),('南京','上海','2026-11-05')]
    assert [s['nights'] for s in t['stays']]==[1,3]
    b=budget(r,[],[{'segment_id':'h1','nightly_price_yuan':100},{'segment_id':'h2','nightly_price_yuan':500}])
    assert sum(x['amount'] for x in b['items'] if x['category']=='accommodation')==1600
    assert sum(x['amount'] for x in b['items'])==b['total']

def test_local_one_day_has_no_transport_or_hotel():
    r=Requirement(departure_city='北京',destinations=['北京'],departure_date='2026-11-01',travel_days=1)
    t=topology(r)
    assert t['local'] and t['legs']==[] and t['stays']==[]
    b=budget(r,[],[])
    assert b['nights']==0 and not any(i['category']=='accommodation' for i in b['items'])

def test_departure_city_in_destination_is_retained():
    r=Requirement(departure_city='上海',destinations=['上海','苏州','苏州'],departure_date='2026-11-01',travel_days=4)
    t=topology(r)
    assert t['cities']==['上海','苏州']
    assert len(t['legs'])==2 and len(t['stays'])==2
    assert t['legs'][0]['date']=='2026-11-02'
