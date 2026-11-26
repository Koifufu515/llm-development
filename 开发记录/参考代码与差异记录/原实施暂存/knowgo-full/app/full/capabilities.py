"""四类能力共用按段并行、候选身份与提交校验；外部失败只影响本段。"""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.full.domain import Requirement, identity, topology
from app.services.providers import query_rail
from app.services.remote import flight_schedule, hotels, amap_driving, find_records, number

CODES=json.loads(Path(__file__).with_name('city_codes.json').read_text())
BRANDS={'economy_hotel':['如家','汉庭','锦江之星'],'star_hotel':['万豪','希尔顿','凯悦'],
        'hostel':['途家民宿','花间堂'],'youth_hostel':['国际青年旅舍（YHA）']}

def available(value):
    value=str(value or '').strip()
    return value in ('有','有票') or bool(re.fullmatch(r'[1-9]\d*(?:张)?',value))

def clock(value):
    match=re.search(r'(\d{2}:\d{2})(?::\d{2})?',str(value or ''))
    return match.group(1) if match else ''

def flight_prices(raw):
    """只接受同一节点明确关联航班号的票价，航线最低价不分摊到每班。"""
    out={}
    def walk(obj,code=None):
        if isinstance(obj,list):
            for row in obj:walk(row,code)
        elif isinstance(obj,dict):
            code=next((str(obj[k]).upper() for k in ('FlightNo','flightNo','flightno','flight_no','flightNumber','flight_number','flight') if obj.get(k)),code)
            if code and re.fullmatch(r'[A-Z0-9]{2}\d{3,4}',code):
                cabin=str(obj.get('cabinclass') or obj.get('cabin') or obj.get('Cabin') or obj.get('cabinCode') or 'Y').upper()
                if cabin in ('Y','ECONOMY','经济舱'):
                    for key in ('price','Price','ticketPrice','ticket_price','adultPrice','fare','lowestPrice'):
                        p=number(obj.get(key))
                        if p is not None and 80<=p<=20000:out[code]=min(out.get(code,p),p)
            for child in obj.values():
                if isinstance(child,(list,dict)):walk(child,code)
    walk(raw);return out

async def quoted_flights(remote,leg):
    multiple={'上海':['SHA','PVG'],'北京':['PEK','PKX'],'成都':['CTU','TFU']}
    dep=multiple.get(leg['from']) or ([CODES['_CITY_AIRPORT'][leg['from']]] if leg['from'] in CODES['_CITY_AIRPORT'] else [])
    arr=multiple.get(leg['to']) or ([CODES['_CITY_AIRPORT'][leg['to']]] if leg['to'] in CODES['_CITY_AIRPORT'] else [])
    if not dep or not arr:return {'status':'unsupported_city','options':[],'message':'机场码未收录，可改选高铁；这不表示该城市没有机场'}
    async def price_query():
        tools=await remote.discover('flight')
        tool=next((t for t in tools if 'getflightpricebycities' in t.name.lower()),None)
        cdep=CODES['_CITY_IATA'].get(leg['from']);carr=CODES['_CITY_IATA'].get(leg['to'])
        if not tool or not cdep or not carr:return {}
        schema=tool.args_schema if isinstance(tool.args_schema,dict) else tool.args_schema.model_json_schema()
        args={}
        for key in schema.get('properties',{}):
            lower=key.lower()
            if 'date' in lower:args[key]=leg['date']
            elif any(s in lower for s in ('arr','dest','to_city','tocity')):args[key]=carr
            elif any(s in lower for s in ('dep','origin','from_city','fromcity')):args[key]=cdep
        if set(schema.get('required',[]))-set(args):return {}
        result=await remote.query('flight',('getflightpricebycities',),args)
        return flight_prices(result.get('data',{})) if result['status']=='ok' else {}
    schedules,prices=await asyncio.gather(asyncio.gather(*(flight_schedule(remote,leg['date'],d,a) for d in dep for a in arr)),price_query())
    options={identity(r['flight_code'],r.get('departure_at'),r.get('from_airport'),r.get('to_airport')):r for result in schedules for r in result.get('options',[])}
    schedule={'status':'ok' if options else 'unavailable' if any(s.get('status')=='unavailable' for s in schedules) else 'empty','source':'Variflight','options':list(options.values()),'airport_pairs':[{'from':d,'to':a} for d in dep for a in arr]}
    for row in schedule.get('options',[]):
        row.update({'option_id':identity(leg, row['flight_code'],row['departure_at'],row.get('from_airport'),row.get('to_airport')),
                    'price_yuan':prices.get(str(row['flight_code']).upper()),
                    'departure_time':clock(row.get('departure_at')),'arrival_time':clock(row.get('arrival_at')),
                    'departure_date':str(row.get('departure_at',''))[:10],'arrival_date':str(row.get('arrival_at',''))[:10],
                    'name':row['flight_code'],'availability':'未提供余座'})
    return schedule

async def transport_segment(services,mode,leg):
    try:
        if mode=='train':
            from app.core.rail import normalize_query,compact_tickets
            from datetime import date
            from zoneinfo import ZoneInfo
            query=normalize_query({}, {'departure_city':leg['from'],'destination':leg['to'],'departure_date':leg['date']},datetime.now(ZoneInfo('Asia/Shanghai')).date())
            tools=services.mcp_manager.tools.get('rail') or await services.mcp_manager.load_service('rail')
            tool=next(t for t in tools if t.name=='get-tickets')
            raw=await asyncio.wait_for(tool.ainvoke({**query,'trainFilterFlags':'GD','format':'json','sortFlag':'startTime','limitedNum':0}),45)
            result=compact_tickets(raw,query,limit=600)
            result['options'].sort(key=lambda o:((o['departure_time']<'17:00') if leg.get('return_leg') else (o['departure_time']<'07:00'),o['departure_time']))
            rows=[]
            for option in result.get('options',[]):
                for seat in option.get('seats',[]):
                    rows.append({**option,'option_id':identity(leg,option['option_id'],seat['name']),
                      'name':option['train_code']+' '+str(seat['name']),'price_yuan':seat['price_yuan'],
                      'availability':str(seat.get('availability') or '未知'),'seat_type':seat['name']})
            result['options']=rows[:30]
        elif mode=='flight': result=await quoted_flights(services.remote,leg)
        else:
            raw=await amap_driving(services.remote,leg['from'],leg['to'])
            def route(obj):
                if isinstance(obj,dict):
                    if 'distance' in obj and ('duration' in obj or 'cost' in obj):return obj
                    for child in obj.values():
                        value=route(child)
                        if value:return value
                elif isinstance(obj,list):
                    for child in obj:
                        value=route(child)
                        if value:return value
                return None
            data=route(raw.get('data',{}));result={'status':'ok' if data else 'unavailable','source':'高德地图','options':[]}
            if data:
                duration=number(data.get('duration') or (data.get('cost') or {}).get('duration'))
                result['options']=[{'option_id':identity(leg,'driving'),'name':'高德默认驾车路线',
                 'distance_km':round((number(data.get('distance')) or 0)/1000,1),
                 'duration_minutes':round(duration/60) if duration is not None else None,
                 'tolls_yuan':number(data.get('tolls') or (data.get('cost') or {}).get('tolls')),
                 'price_yuan':None,'availability':'路线查询成功','note':'未核实油费、停车费与完整驾驶成本'}]
        stamp=result.get('queried_at') or datetime.now(timezone.utc).isoformat()
        for row in result.get('options',[]):row.update({**leg,'mode':mode,'source':result.get('source',mode),'queried_at':stamp})
        return {**leg,'mode':mode,**result}
    except Exception:
        return {**leg,'mode':mode,'status':'unavailable','options':[],'message':'该段查询失败，其余段照常保留'}

async def transport_payload(services,req):
    t=topology(req);mode=req.transport_types[0]
    async def one(leg,i):
        leg={**leg,'return_leg':i==len(t['legs'])-1 and leg['to']==req.departure_city}
        if len(req.transport_types)==1:return await transport_segment(services,mode,leg)
        alternatives=await asyncio.gather(*(transport_segment(services,m,leg) for m in req.transport_types))
        options=[o for result in alternatives for o in result.get('options',[])]
        return {**leg,'mode':'mixed','options':options,'status':'ok' if options else 'unavailable','alternatives':[{k:r.get(k) for k in ('mode','status','message')} for r in alternatives]}
    segments=await asyncio.gather(*(one(leg,i) for i,leg in enumerate(t['legs'])))
    return {'skill_name':mode+'_multi_segment','mode':'mixed' if len(req.transport_types)>1 else mode,'priority':req.transport_types,'segments':list(segments)}

async def hotel_payload(services,req):
    async def one(stay):
        row=await hotels(services.remote,stay['city'],stay['checkin'],stay['nights'],min(req.adult_count,2),int(stay['segment_id'][1:]),preference=req.accommodation_types[0] if req.accommodation_types else 'economy_hotel')
        opts=[]
        for option in row.get('options',[]):
            p=option.get('nightly_price_yuan')
            if option.get('distance_meters') is not None and option['distance_meters']>15000:continue
            if p is not None and p<25: continue
            opts.append({**option,'option_id':identity(stay,option['name'],option.get('address')),
                         **stay,'mode':'hotel','source':'AIGOHOTEL','queried_at':row.get('queried_at')})
        if not opts:
            opts=[{**stay,'option_id':identity(stay,'brand',name),'name':name,'mode':'brand',
                   'nightly_price_yuan':None,'source':'品牌参考','note':'仅为常见品牌，不表示该城存在可订门店或实时报价'}
                  for name in BRANDS[req.accommodation_types[0] if req.accommodation_types else 'economy_hotel']]
        return {**stay,'mode':opts[0]['mode'],'options':opts,'status':row['status'],'message':row.get('message','')}
    segments=await asyncio.gather(*(one(stay) for stay in topology(req)['stays']))
    return {'skill_name':'hotel_multi_segment','mode':'hotel','segments':list(segments)}

def auto_pick(payload):
    choices=[]
    for index,segment in enumerate(payload['segments']):
        options=segment['options']
        if not options: continue
        if payload['mode']=='mixed':
            for candidate_mode in payload.get('priority',['train','flight','driving']):
                choices_for_mode=auto_pick({'mode':candidate_mode,'segments':[{**segment,'options':[o for o in options if o['mode']==candidate_mode]}]})
                if choices_for_mode:
                    choices.extend(choices_for_mode);break
            continue
        if payload['mode']=='train':
            valid=[o for o in options if available(o.get('availability'))]
            same_day=[o for o in valid if o.get('arrival_date')==o.get('date')]
            if same_day:valid=same_day
            if segment.get('return_leg') or index==len(payload['segments'])-1 and len(payload['segments'])>1:
                late=[o for o in valid if o.get('departure_time','')>='17:00']
                if late:valid=late
            def score(o):
                h,m=map(int,o.get('duration','99:59').split(':'))
                return h*60+m+(o.get('price_yuan') if o.get('price_yuan') is not None else 500)/10
            row=min(valid,key=score) if valid else None
        elif payload['mode']=='hotel':
            valid=[o for o in options if o.get('nightly_price_yuan') is not None]
            row=min(valid,key=lambda o:o['nightly_price_yuan']) if valid else options[0]
        elif payload['mode']=='flight':
            valid=options
            if segment.get('return_leg') or index==len(payload['segments'])-1 and len(payload['segments'])>1:
                late=[o for o in options if o.get('departure_time','')>='17:00']
                if late:valid=late
            else:
                early=[o for o in options if o.get('arrival_time','99:99')<='12:00']
                if early:valid=early
            row=min(valid,key=lambda o:(o['price_yuan'] is None,o['price_yuan'] or 0,o.get('departure_time','')))
        else: row=options[0]
        if row: choices.append({'segment_id':segment['segment_id'],'option_id':row['option_id']})
    return choices

def validate_selection(payload,selections):
    expected={s['segment_id']:s for s in payload['segments']};seen=set();picked=[]
    for choice in selections:
        sid=choice.get('segment_id')
        if sid in seen:raise ValueError('同一段不能重复提交')
        seen.add(sid)
        segment=expected.get(sid)
        if not segment:raise ValueError('选择包含未知行程段')
        row=next((o for o in segment['options'] if o['option_id']==choice.get('option_id')),None)
        if row is None:raise ValueError('选项不在本轮候选里，请重新选择')
        if row.get('mode',payload['mode'])=='train' and not available(row.get('availability')):
            raise ValueError('该席别无现票或仅可候补，请选择其他候选')
        picked.append(row)
    required={sid for sid,s in expected.items() if any(o.get('mode',payload['mode'])!='train' or available(o.get('availability')) for o in s['options'])}
    if required-seen:raise ValueError('请选完所有有现票候选的行程段')
    return picked
