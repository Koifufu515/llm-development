"""凭证按服务隔离；只注册只读查询，不把模型Key交给第三方MCP。"""
import asyncio,json,hashlib,re
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.config import Settings
from app.core.rail import content_text

class RemoteProviders:
    def __init__(self):self.tools={};self.fingerprints={};self.locks={}
    async def discover(self,name):
        lock=self.locks.setdefault(name,asyncio.Lock())
        async with lock:
            settings=Settings()
            entries={
              'hotel':(settings.aigohotel_mcp_api,'https://mcp.aigohotel.com/mcp','bearer'),
              'flight':(settings.variflight_api_key,'https://ai.variflight.com/servers/aviation/mcp/','api_key'),
              'amap':(settings.amap_api_key,'https://mcp.amap.com/mcp','key'),
              'search':(settings.dashscope_api_key,'https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp','bearer')}
            secret,url,auth=entries[name];key=secret.get_secret_value().strip()
            if not key:return []
            digest=hashlib.sha256(key.encode()).hexdigest()
            if self.fingerprints.get(name)==digest and name in self.tools:return self.tools[name]
            cfg={'transport':'streamable_http','url':url}
            if auth=='bearer':cfg['headers']={'Authorization':'Bearer '+key}
            else:
                from urllib.parse import urlencode
                cfg['url']+='?'+urlencode({auth:key})
            try:
                client=MultiServerMCPClient({name:cfg})
                tools=await asyncio.wait_for(client.get_tools(),25)
                self.tools[name]=tools;self.fingerprints[name]=digest
                return tools
            except Exception:
                self.tools.pop(name,None);return []

    async def query(self,service,hints,arguments):
        tools=await self.discover(service)
        tool=next((t for t in tools if any(h in t.name.lower() for h in hints)),None)
        if tool is None:return {'status':'unavailable','code':'service_not_ready','message':'服务凭证未配置或工具不可用'}
        try:
            result=await asyncio.wait_for(tool.ainvoke(arguments),45)
            text=content_text(result)
            if len(text)>500000:return {'status':'unavailable','code':'oversized_response','message':'返回数据超过处理上限'}
            try:data=json.loads(text)
            except ValueError:
                positions=[i for mark in ('{','[') if (i:=text.find(mark))>=0]
                if positions:text=text[min(positions):]
                # Variflight原接口存在Python字典文本；仅literal_eval，不执行代码。
                import ast
                data=ast.literal_eval(text)
            return {'status':'ok','data':data,'tool':tool.name,'source':service,
                'queried_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}
        except Exception:return {'status':'unavailable','code':'query_failed','message':'外部查询失败或结果格式不支持'}


def find_records(value,name_keys,detail_keys,depth=0):
    if depth>8:return []
    if isinstance(value,list):
        rows=[x for x in value if isinstance(x,dict) and any(x.get(k) for k in name_keys) and any(k in x for k in detail_keys)]
        if rows:return rows
        return next((found for x in value if (found:=find_records(x,name_keys,detail_keys,depth+1))),[])
    if isinstance(value,dict):
        return next((found for x in value.values() if (found:=find_records(x,name_keys,detail_keys,depth+1))),[])
    return []


def number(value):
    if isinstance(value,bool):return None
    try:
        n=float(value)
        return n if 0<=n<1000000 else None
    except (ValueError,TypeError):return None

async def hotels(remote,city,day,nights,adults,index=0,preference=None):
    if nights<=0:return {'status':'not_needed','city':city,'options':[],'message':'该站不住宿'}
    result=await remote.query('hotel',('searchhotels','find-hotels'),{
        'originQuery':f'{city}住宿 {nights}晚 {adults}人 '+({'economy_hotel':'经济型酒店','star_hotel':'四五星酒店','hostel':'特色民宿','youth_hostel':'青年旅舍'}.get(preference,'')),'place':city+' 中国','placeType':'城市',
        'checkInParam':{'checkInDate':day,'stayNights':nights,'adultCount':adults},
        'filterOptions':{'starRatings':[4,5] if preference=='star_hotel' else [0,3] if preference=='economy_hotel' else [0,5]},'size':15})
    result.update({'city':city,'nights':nights})
    if result['status']!='ok':
        result['options']=[];result['message']='实时酒店不可用，住宿按用户填写的预算估算。';return result
    rows=find_records(result['data'],('hotelName','name','hotel_name'),('pricePerNight','price','totalPrice','starRating','address'))
    options=[]
    for j,row in enumerate(rows[:15]):
        name=next((str(row[k]) for k in ('hotelName','name','hotel_name') if row.get(k)),None)
        nightly=number(row.get('pricePerNight'));total=number(row.get('totalPrice'))
        if nightly is None and isinstance(row.get('price'),(int,float,str)):nightly=number(row['price'])
        if nightly is None and total is not None:nightly=total/nights
        price=row.get('price')
        if isinstance(price,dict) and price.get('hasPrice') is True and price.get('currency')=='CNY':
            if nightly is None:nightly=number(price.get('lowestPrice'))
            # 实际供应商明确给出lowestPrice为每晚，并在message中显示总价。
            match=re.search(r'(?:总价[：:]?\s*)([0-9]+(?:\.[0-9]+)?)\s*CNY',str(price.get('message','')))
            if total is None and match:total=number(match.group(1))
        if total is None and nightly is not None:total=nightly*nights
        options.append({'option_id':f'h{index}-{j+1}','name':name,'nightly_price_yuan':nightly,'stay_total_yuan':total,
                        'address':row.get('address'),'rating':row.get('starRating'),'distance_meters':number(row.get('distanceInMeters')),'source':'AIGOHOTEL','currency':'CNY'})
    # 原始价格口径不明时仅留名称，不把0作为未知价格。
    result['options']=options;result.pop('data',None)
    result['status']='ok' if options else 'unavailable'
    result['message']='已查询实时酒店，价格及可订状态以供应商为准' if options else '酒店结果未解析出可验证候选，使用预算估算'
    return result

async def flight_schedule(remote,day,departure_airport,arrival_airport):
    result=await remote.query('flight',('searchflightsbydeparr',),{'date':day,'dep':departure_airport,'arr':arrival_airport,'limit':12,'detail':'summary'})
    if result['status']!='ok':return result
    rows=find_records(result['data'],('FlightNo','flightNo','flight_no'),('FlightDeptimePlanDate','FlightDepAirport','FlightArrAirport','departureTime'))
    options=[]
    for row in rows[:12]:
        code=row.get('FlightNo') or row.get('flightNo') or row.get('flight_no')
        dep=row.get('FlightDeptimePlanDate') or row.get('departureTime')
        arr=row.get('FlightArrtimePlanDate') or row.get('arrivalTime')
        identity='|'.join([str(code),str(dep),arrival_airport])
        options.append({'option_id':hashlib.sha256(identity.encode()).hexdigest()[:20],'flight_code':code,
           'from_airport':departure_airport,'to_airport':arrival_airport,'departure_at':dep,'arrival_at':arr,
           'price_yuan':None,'currency':'CNY','note':'仅时刻表，未获取可核对票价；不代表已预订'})
    result['options']=options;result['status']='ok' if options else 'empty'
    result.pop('data',None)
    return result

async def driving_route(departure,destination):
    import httpx
    key=Settings().tencent_map_key.get_secret_value().strip()
    if not key:return {'status':'unavailable','message':'腾讯地图Key未配置'}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            async def geocode(city):
                response=await client.get('https://apis.map.qq.com/ws/geocoder/v1/',params={'address':city,'key':key})
                response.raise_for_status();body=response.json()
                if body.get('status')!=0:return {'error_code':body.get('status'),'error_message':body.get('message')}
                loc=body['result']['location'];return f"{loc['lat']},{loc['lng']}"
            start,end=await asyncio.gather(geocode(departure),geocode(destination))
            if isinstance(start,dict) or isinstance(end,dict):
                err=start if isinstance(start,dict) else end
                return {'status':'unavailable','source':'腾讯地图',**err,'message':'腾讯地图查询失败：'+str(err['error_message'])}
            response=await client.get('https://apis.map.qq.com/ws/direction/v1/driving/',params={'from':start,'to':end,'key':key})
            response.raise_for_status();body=response.json()
            if body.get('status')!=0:raise ValueError('routing unavailable')
            route=body['result']['routes'][0]
            return {'status':'ok','source':'腾讯地图','from':departure,'to':destination,'distance_meters':route.get('distance'),
                    'duration_minutes':route.get('duration'),'toll_yuan':route.get('toll'),'price_yuan':None,
                    'queried_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'note':'城市中心点路线，实际起终点未指定；不含油费、停车或完整行车费用。'}
    except Exception:return {'status':'unavailable','message':'腾讯地图地理编码或路线请求失败，请检查Key权限与配额'}

async def amap_driving(remote,departure,destination):
    async def geo(city):
        r=await remote.query('amap',('maps_geo',),{'address':city})
        if r['status']!='ok':return None
        value=r['data']
        if isinstance(value,dict):
            rows=value.get('results') or value.get('geocodes') or []
            if not rows and isinstance(value.get('return'),dict):rows=value['return'].get('geocodes',[])
            if rows:return rows[0].get('location')
        return None
    start,end=await asyncio.gather(geo(departure),geo(destination))
    if not start or not end:return {'status':'unavailable','source':'高德','message':'城市坐标解析失败'}
    return await remote.query('amap',('maps_direction_driving',),{'origin':start,'destination':end})
