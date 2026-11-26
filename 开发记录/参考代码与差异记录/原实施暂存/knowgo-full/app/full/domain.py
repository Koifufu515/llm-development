"""所有通道共用的日期、需求、结构和预算口径。"""
import hashlib
import math
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

STEPS = ['requirement_collection', 'destination_recommendation', 'transport_planning',
         'accommodation_planning', 'food_planning', 'itinerary_generation', 'budget_summarization']
LABELS = dict(zip(STEPS, ['需求收集','目的地推荐','交通规划','住宿规划','餐饮偏好','行程生成','预算汇总']))
TRANSPORTS = Literal['train','flight','driving']


class Requirement(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    departure_city: str = Field(min_length=1, max_length=50)
    destinations: list[str] = Field(default_factory=list, max_length=8)
    departure_date: date
    travel_days: int = Field(ge=1, le=30)
    adult_count: int = Field(default=1, ge=1, le=20)
    children_count: int = Field(default=0, ge=0, le=20)
    budget_max: float = Field(default=0, ge=0, le=1000000, allow_inf_nan=False)
    transport_types: list[TRANSPORTS] = Field(default_factory=lambda:['train'], min_length=1, max_length=3)
    accommodation_types: list[Literal['economy_hotel','star_hotel','hostel','youth_hostel']] = Field(default_factory=lambda:['economy_hotel'])
    food_preferences: list[Literal['specialty','chain','local']] = Field(default_factory=lambda:['local','specialty'])
    travel_styles: list[str] = Field(default_factory=list, max_length=8)
    special_needs: str = Field(default='', max_length=1000)
    auto_confirm: bool = False
    city_days: list[int] | None = None

    @model_validator(mode='after')
    def valid_cities(self):
        self.destinations = list(dict.fromkeys(c.strip() for c in self.destinations if c.strip()))
        if any(len(c)>50 for c in self.destinations): raise ValueError('城市名称过长')
        if self.destinations and self.travel_days < len(self.destinations):
            raise ValueError('每天至少分配一座城市，请增加天数或减少目的地')
        if self.city_days is not None:
            if len(self.city_days)!=len(self.destinations) or any(d<1 for d in self.city_days) or sum(self.city_days)!=self.travel_days:
                raise ValueError('各城天数必须与城市一一对应且合计等于总天数')
        return self


def topology(req: Requirement) -> dict:
    """天数是游玩日期数量；住宿是相邻日期间夜晚，始终合计N−1。"""
    cities = req.destinations
    if not cities: raise ValueError('请先确定目的地')
    if req.city_days:
        counts = req.city_days
    else:
        per, rem = divmod(req.travel_days, len(cities))
        counts = [per + (i < rem) for i in range(len(cities))]
    first = req.departure_date
    end = first + timedelta(days=req.travel_days-1)
    windows=[]; days=[]; legs=[]; cursor=first; previous=req.departure_city
    for i,(city,count) in enumerate(zip(cities,counts)):
        if city != previous:
            legs.append({'segment_id':f's{len(legs)+1}','from':previous,'to':city,'date':cursor.isoformat()})
        next_day=cursor+timedelta(days=count)
        checkout=min(next_day,end)
        nights=max((checkout-cursor).days,0)
        windows.append({'segment_id':f'h{i+1}','city':city,'checkin':cursor.isoformat(),
                        'checkout':checkout.isoformat(),'nights':nights,'days':count})
        offset=len(days)
        days.extend({'day':offset+j+1,'city':city,'date':(cursor+timedelta(days=j)).isoformat()} for j in range(count))
        previous=city;cursor=next_day
    if previous!=req.departure_city:
        legs.append({'segment_id':f's{len(legs)+1}','from':previous,'to':req.departure_city,'date':end.isoformat()})
    assert sum(w['nights'] for w in windows)==req.travel_days-1
    return {'cities':cities,'days':days,'legs':legs,'stays':[w for w in windows if w['nights']>0],
            'windows':windows,'return_date':end.isoformat(),'local':not legs}


def identity(*parts) -> str:
    return hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:24]


class Activity(BaseModel):
    model_config=ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=2,max_length=100)
    kind: Literal['attraction','meal','hotel','transport','free']
    description: str = Field(min_length=15,max_length=600)
    start_time: str = Field(pattern=r'^(?:[01]\d|2[0-3]):[0-5]\d$')
    end_time: str = Field(pattern=r'^(?:[01]\d|2[0-3]):[0-5]\d$')
    source_ids: list[str] = Field(default_factory=list,max_length=6)
    @model_validator(mode='after')
    def time_order(self):
        if self.end_time<self.start_time: raise ValueError('活动结束不得早于开始')
        return self


class DayBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    day: int = Field(ge=1,le=30)
    city: str
    morning: list[Activity] = Field(min_length=1,max_length=3)
    noon: list[Activity] = Field(min_length=1,max_length=3)
    afternoon: list[Activity] = Field(min_length=1,max_length=3)
    evening: list[Activity] = Field(min_length=1,max_length=3)
    tips: list[str] = Field(min_length=1,max_length=4)


class ItineraryBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    title: str = Field(min_length=2,max_length=120)
    days: list[DayBody] = Field(min_length=1,max_length=30)


def validate_body(body: ItineraryBody, req: Requirement, selected: list[dict]) -> None:
    expected=topology(req)['days']
    if [(d.day,d.city) for d in body.days] != [(d['day'],d['city']) for d in expected]:
        raise ValueError('天序号、城市或总天数与已确认需求不一致')
    for day in body.days:
        acts=[a for slot in ('morning','noon','afternoon','evening') for a in getattr(day,slot)]
        for a,b in zip(acts,acts[1:]):
            if b.start_time<a.end_time: raise ValueError(f'第{day.day}天活动时间重叠')
        from datetime import datetime,time
        day_date=date.fromisoformat(expected[day.day-1]['date'])
        for transport in selected:
            if not transport:continue
            dep=transport.get('departure_time');arr=transport.get('arrival_time')
            planned=date.fromisoformat(transport.get('date') or expected[day.day-1]['date'])
            dep_date=date.fromisoformat((transport.get('departure_date') or planned.isoformat())[:10])
            arr_date=date.fromisoformat((transport.get('arrival_date') or planned.isoformat())[:10])
            if not dep or not arr:continue
            dep_at=datetime.combine(dep_date,time.fromisoformat(dep));arr_at=datetime.combine(arr_date,time.fromisoformat(arr))
            for a in acts:
                if a.kind in ('transport','free'):continue
                start=datetime.combine(day_date,time.fromisoformat(a.start_time));end=datetime.combine(day_date,time.fromisoformat(a.end_time))
                if transport.get('to')==day.city and planned<=day_date<=arr_date and start<arr_at:
                    raise ValueError(f'第{day.day}天在到达{day.city}前安排了游玩')
                if transport.get('from')==day.city and day_date==dep_date and end>dep_at:
                    raise ValueError(f'第{day.day}天出发后仍安排了原城市活动')


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def budget(req: Requirement, transport: list[dict], lodging: list[dict]) -> dict:
    people=req.adult_count+req.children_count;rooms=math.ceil(people/2);items=[]
    picks={x['segment_id']:x for x in transport if x}
    stays={x['segment_id']:x for x in lodging if x}
    topo=topology(req)
    for leg in topo['legs']:
        row=picks.get(leg['segment_id'],{});price=row.get('price_yuan')
        driving=row.get('mode',req.transport_types[0])=='driving'
        if driving:
            distance=row.get('distance_km');tolls=row.get('tolls_yuan')
            rate=price if price is not None else money((distance*.65 if distance is not None else 300)+(tolls or 0))
            quantity=1
            note='按整车估算油费0.65元/公里，加已返回过路费；不含停车费，不表示实际车辆成本' if price is None else '整车查询参考价，尚未预订'
        else:
            rate=price if price is not None else 500;quantity=people
            note='尚未预订；儿童暂按成人参考价，优惠以购票时为准'
        items.append({'category':'transport','label':leg['from']+'→'+leg['to'],'segment_id':leg['segment_id'],
          'unit':'车' if driving else '人','quantity':quantity,'unit_price':rate,
          'amount':money(rate*quantity),'basis':'quote' if price is not None else 'estimate','source':row.get('source','规划估算'),
          'queried_at':row.get('queried_at'),'note':note})
    for stay in topo['stays']:
        row=stays.get(stay['segment_id'],{});nightly=row.get('nightly_price_yuan');rate=nightly if nightly is not None else 300
        items.append({'category':'accommodation','label':stay['city']+'住宿','segment_id':stay['segment_id'],
          'unit':'间夜','quantity':stay['nights']*rooms,'unit_price':rate,'amount':money(rate*stay['nights']*rooms),
          'basis':'quote' if nightly is not None else 'estimate','source':row.get('source','规划估算'),
          'queried_at':row.get('queried_at'),'note':f"{stay['nights']}晚×{rooms}间；品牌参考不表示可订门店"})
    for key,label,rate in [('food','餐饮',150),('attractions','门票',200),('misc','市内交通及杂费',100)]:
        items.append({'category':key,'label':label,'unit':'人天','quantity':people*req.travel_days,
                      'unit_price':rate,'amount':money(rate*people*req.travel_days),'basis':'estimate','source':'规划估算'})
    total=money(sum(x['amount'] for x in items));pp=money(total/people)
    return {'currency':'CNY','items':items,'total':total,'per_person':pp,'people':people,'rooms':rooms,
            'nights':req.travel_days-1,'budget_max':req.budget_max,'over_budget':bool(req.budget_max and pp>req.budget_max),
            'quote_total':money(sum(x['amount'] for x in items if x['basis']=='quote')),
            'estimate_total':money(sum(x['amount'] for x in items if x['basis']=='estimate')),
            'notice':'报价为查询时参考价，估算单独列示；本系统不执行购票、订房或支付。'}
