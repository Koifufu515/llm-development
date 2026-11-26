from pydantic import BaseModel,Field

# ============== 前端 TravelItinerary 契约结构（字段名与网页端严格一致） ==============

class ScenicSpot(BaseModel):
    """景点"""
    toponym: str = Field(description="景点名称")
    toponym_desc: str = Field(description="景点介绍，50-100字")
    toponym_image: str = Field(description="封面图 URL，无则空字符串")
    toponym_image_list: list[str] = Field(description="图片列表，无则空数组")
    longitude: float | None = Field(default=None, description="经度")
    latitude: float | None = Field(default=None, description="纬度")

class ItineraryItem(BaseModel):
    """时段安排"""
    time: str = Field(description="时段，如：上午/下午/晚上")
    scenic_spots_list: list[ScenicSpot]

class ItineraryDay(BaseModel):
    """一天"""
    id: str = Field(description="唯一标识，随机字符串")
    day: str = Field(description="第几天，如：第一天")
    itinerary: list[ItineraryItem]
    route_polylines: list[list[float]] = Field(default_factory=list)  # 每段驾车路线平铺坐标 [lat,lng,...]（高德方向API）

# ★ 四层嵌套对着前端组件层级；字段名与前端 TSX 逐字一致，改一个前端就崩
class TravelItinerary(BaseModel):
    """行程清单（前端渲染契约）"""
    title: str = Field(description="行程标题")
    itinerary_list: list[ItineraryDay]


def plan_to_contract(plan):
    """原TravelItinerary四层字段契约；坐标/图片只取真实查到的地点，不让模型再编一次。"""
    days=[];points=plan.map_data.get('points',[])
    for day in plan.body['days']:
        slots=[]
        for key,label in [('morning','上午'),('noon','中午'),('afternoon','下午'),('evening','晚上')]:
            spots=[]
            for activity in day[key]:
                point=next((p for p in points if p['day']==day['day'] and p.get('source_activity')==activity['name']),{})
                image=point.get('photo_url') or ''
                spots.append(ScenicSpot(toponym=activity['name'],toponym_desc=activity['description'],toponym_image=image,toponym_image_list=[image] if image else [],longitude=point.get('lng'),latitude=point.get('lat')))
            slots.append(ItineraryItem(time=label,scenic_spots_list=spots))
        routes=[r['coordinates'] for r in plan.map_data.get('routes',[]) if r['day']==day['day']]
        days.append(ItineraryDay(id=plan.id+'-d'+str(day['day']),day='第'+str(day['day'])+'天',itinerary=slots,route_polylines=[[n for pair in coords for n in pair] for coords in routes]))
    return TravelItinerary(title=plan.title,itinerary_list=days).model_dump()
