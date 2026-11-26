from app.full.domain import Requirement,topology

def test_original_express_extends_short_multicity_and_preserves_notice():
 r=Requirement(departure_city='上海',destinations=['苏州','杭州','南京'],departure_date='2026-11-01',travel_days=2,auto_confirm=True)
 assert r.travel_days==6 and r.requested_travel_days==2
 restored=Requirement.model_validate(r.model_dump(mode='json'))
 assert restored.requested_travel_days==2 and len(topology(restored)['days'])==6

def test_manual_explicit_city_days_not_silently_extended():
 r=Requirement(departure_city='上海',destinations=['苏州','杭州'],departure_date='2026-11-01',travel_days=2,auto_confirm=True,city_days=[1,1])
 assert r.travel_days==2 and r.requested_travel_days is None
