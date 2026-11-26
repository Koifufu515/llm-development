"""原文0409/0413/0418：60字、缺日/缺城市/空时段/重复越界/末日返程。
原文模板仅作已标注的通用补位，不当作已核实POI或实时报价。
"""
from typing import Annotated
from pydantic import BaseModel,Field,model_validator,ValidationInfo

# ============== 行程正文结构化（Pydantic） ==============
_SLOT_KEYS = ("morning", "noon", "afternoon", "evening")
_SLOT_LABELS = {"morning": "上午", "noon": "中午", "afternoon": "下午", "evening": "晚上"}
_RETURN_HINTS = ("返程", "返回", "回程")
_ITEM_MIN_CHARS = 60

PlanItem = Annotated[str, Field(min_length=1)]

class DayPlan(BaseModel):
    """单日行程：分4个时段，配套当日小贴士"""
    day: int = Field(ge=1, description="第几天（从1开始，连续覆盖1~旅行天数）")
    city: str = Field(default="", description="当天所在城市，如“重庆”")
    morning: list[PlanItem] = Field(min_length=1, description="上午安排（1~2条，含玩法/看点/门票或耗时）")
    noon: list[PlanItem] = Field(min_length=1, description="中午安排（1~2条，午餐写店名+招牌菜+人均）")
    afternoon: list[PlanItem] = Field(min_length=1, description="下午安排（1~2条，含玩法与建议停留时长）")
    evening: list[PlanItem] = Field(min_length=1, description="晚上安排（1~2条；末日晚上必须含返程）")
    tips: list[PlanItem] = Field(default_factory=list, description="当天实用小贴士（1~3条：门票/预约/交通接驳/避坑）")

class ItineraryBody(BaseModel):
    """完整行程结构化模型，校验天数连续性、条目长度、末日返程规则"""
    days: list[DayPlan] = Field(min_length=1, description="逐日行程列表，按天序号升序")

    @model_validator(mode="after")
    def _check_days(self, info: ValidationInfo) -> "ItineraryBody":
        nums = [d.day for d in self.days]
        if len(set(nums)) != len(nums):
            raise ValueError(f"天序号重复：{sorted(nums)}，每天只能出现一次")

        need = (info.context or {}).get("travel_days") or 0

        for d in self.days:
            if not d.tips:
                raise ValueError(f"第 {d.day} 天缺少 tips：每天至少 1 条实用小贴士（预约/门票/交通接驳/避坑）")
            for key in _SLOT_KEYS + ("tips",):
                for item in getattr(d, key):
                    if len(str(item).strip()) >= _ITEM_MIN_CHARS:
                        continue
                    raise ValueError(
                        f"第 {d.day} 天「{_SLOT_LABELS.get(key, '小贴士')}」的条目「{str(item).strip()}」"
                        f"只有 {len(str(item).strip())} 字：每条不少于 {_ITEM_MIN_CHARS} 字"
                        f"（时间/地点 + 玩法或看点 + 价格或时长）"
                    )

        if not need:
            return self

        miss = [d for d in range(1, need + 1) if d not in nums]
        if miss:
            raise ValueError(f"缺少第 {'、'.join(str(d) for d in miss)} 天：必须恰好覆盖第 1~{need} 天")
        if max(nums) > need:
            raise ValueError(f"超出旅行天数：全程仅 {need} 天，却出现第 {max(nums)} 天")

        tail = next((d for d in self.days if d.day == need), None)
        if tail and not any(h in " ".join(tail.evening) for h in _RETURN_HINTS):
            raise ValueError(f"第 {need} 天（末日）晚上必须包含返程安排，如“乘 G1710 返回天津”")
        return self


_ITINERARY_FILL: dict[str, tuple[str, ...]] = {
    "morning": (
        "{city}市区漫步或就近景点游览（09:00 出发），按体力灵活安排，建议停留 1~2 小时，多数免费开放；沿途可顺路打卡当地老街区与公园，注意补水与防晒，返程预留 30 分钟交通时间",
        "上午到{city}人气街区与公园慢逛（09:30 前后出门），以拍照歇脚为主，用时约 2 小时，花费可控；建议先查当日开放时间与是否需要预约，人多时可改走周边支路避开人流",
    ),
    "noon": (
        "{city}就近选一家本地口碑餐馆用餐（12:00 前后），人均约 50 元，避开景点门口高价店，饭后稍作休息；点单前可先看评分与招牌菜，人多时取号后到周边逛一圈再回",
        "午餐在{city}商圈内解决（12:30 前后），优先本地小吃组合，人均约 40 元，吃完原地休息半小时；商圈内餐饮选择多，可先转一圈比价再决定，避免在景区门口就餐",
    ),
    "afternoon": (
        "{city}街区闲逛或咖啡馆休整（14:00 开始），可挑周边小景点补充参观，建议停留 2 小时，多数无需门票；午后气温较高，建议室内外交替安排，并留意景点闭馆时间",
        "下午安排{city}特色展馆或水岸步道（14:30 前后），以免费预约场馆为主，用时约 2 小时，注意闭馆时间；展馆多需提前一天线上预约，出发前再核实一次当日开放安排",
    ),
    "evening": (
        "{city}就近晚餐后返回住处休息（18:00 前后），人均约 60 元，留意末班地铁与公交时间；餐后可散步消食，夜间出行尽量走主干道，保管好随身财物",
        "晚上在{city}夜市或步行街觅食（18:30 前后），人均约 50 元，饭后早点回住处，方便次日出行；夜市人流密集，注意随身物品，返程优先地铁或正规网约车",
    ),
}

def _fill_item(key: str, day: int, city: str) -> str:
    """空缺时段补位条目，按天轮换文案并填充对应城市，避免多天重复"""
    variants = _ITINERARY_FILL.get(key) or (
        "{city}自由活动，按现场情况灵活安排，注意留出交通时间；可就近逛逛街区或公园，"
        "人均花费可控，建议提前把当日行程与次日出发时间对齐",
    )
    return variants[(max(1, day) - 1) % len(variants)].replace("{city}", city or "当地")

_FILL_TIPS: tuple[str, ...] = (
    "提前查询景点开放时间与预约要求，避免现场排队；市内出行优先地铁并避开早晚高峰，"
    "热门景点建议提前 3~7 天线上实名预约，随身携带身份证以备核验",
    "当天行程较松，可临时加一处顺路小景点；随身带好身份证、充电宝与常用药品，"
    "注意天气变化，雨季备好雨具，早晚温差大时及时增减衣物",
)

def _fill_tip(day: int, city: str) -> str:
    """空缺小贴士补位条目，按天轮换文案，避免多天重复"""
    return f"{city or '当地'}：{_FILL_TIPS[(max(1, day) - 1) % len(_FILL_TIPS)].strip()}"

_ITEM_PAD = "（建议停留 1~2 小时，具体开放时间与预约要求请以官方当日公告为准，务必提前一天在官方渠道核实，并预留往返交通与排队时间）"
_BACK_PAD = "，请提前 1 小时到站取票安检，按已确认的车次/航班对号入座乘车返程，到站后留意行李并预留换乘与出站时间，途中如遇晚点请及时与酒店沟通入住时间"
_TIP_PAD = "，请提前在官方渠道核实预约要求与开放时间，旺季建议提前 3~7 天抢票，并留意当日临时闭馆或限流公告，出行前再次确认以免白跑"



def _normalize_itinerary_days(
    days: list[dict], need: int, back_text: str = "", cities: list[str] | None = None
) -> tuple[list[dict], list[str]]:
    """按旅行天数归一化逐日结构：只补空缺、只裁非法，不改写模型已给出的有效内容

 补位条目按天轮换 + 写入当天城市（cities 由 _day_city_map 供），
    并给漏填 city 的天补上城市标注（此前 Day5/Day6 无城市标注、多天出现同一条补位文案）
    """
    fixes: list[str] = []
    kept: dict[int, dict] = {}
    for raw in days or []:
        if not isinstance(raw, dict):
            continue
        try:
            day = int(raw.get("day") or 0)
        except (TypeError, ValueError):
            continue
        if day < 1 or (need and day > need) or day in kept:
            fixes.append(f"忽略第 {day} 天（越界或重复）")
            continue
        kept[day] = raw
    total = need or (max(kept) if kept else 1)
    out: list[dict] = []
    for day in range(1, total + 1):
        d = dict(kept.get(day) or {})
        d["day"] = day
        if not str(d.get("city") or "").strip() and cities and 0 < day <= len(cities):
            d["city"] = cities[day - 1]
            fixes.append(f"补第 {day} 天城市（{cities[day - 1]}）")
        if day not in kept:
            fixes.append(f"补第 {day} 天")
        last = bool(need) and day == need
        for key in _SLOT_KEYS:
            items = [str(x).strip() for x in (d.get(key) or []) if str(x).strip()]
            items = [x if len(x) >= _ITEM_MIN_CHARS else x + _ITEM_PAD for x in items]
            # 只在**空时段**补位（floor=1）——模型已给出内容的时段原样保留，
            # 不再为凑"≥2 条"追加通用句（同槽两条并列会被读成重复安排）
            floor = 1  # ★ 只给空时段补位：模型已给内容的时段原样保留
            while len(items) < floor:
                items.append(_fill_item(key, day, str(d.get("city") or "")))
                fixes.append(f"补第 {day} 天{_SLOT_LABELS[key]}")
            d[key] = items
        tips = [str(x).strip() for x in (d.get("tips") or []) if str(x).strip()]
        tips = [x if len(x) >= _ITEM_MIN_CHARS else x + _TIP_PAD for x in tips]
        d["tips"] = tips or [_fill_tip(day, str(d.get("city") or ""))]
        if not tips:
            fixes.append(f"补第 {day} 天小贴士")
        if last and not any(h in " ".join(d["evening"]) for h in _RETURN_HINTS):
            back = back_text or "傍晚按已确认的交通班次返程"
            if len(back) < _ITEM_MIN_CHARS:  # 短句会被长度校验拦下，代码补足
                back += _BACK_PAD
            d["evening"] = d["evening"] + [back]
            fixes.append(f"补第 {day} 天返程")
        out.append(d)
    return out, fixes


def normalize_enhanced_body(payload,req,transports):
    """复用原文字符串归一化，保留增强Activity中已存在的地点、时间和来源。
    原始有效内容不替换；新增通用项显式标为待确认，使用空时段中的零时长占位。
    返回原schema正文，增强schema正文，以及全部补位动作。
    """
    from copy import deepcopy
    from app.full.domain import topology
    source=deepcopy(payload);raws=source.get('days') or [];need=req.travel_days
    originals={};plain=[]
    for day in raws:
        if not isinstance(day,dict):continue
        try:n=int(day.get('day') or 0)
        except (ValueError,TypeError):continue
        if n in originals or n<1 or n>need:
            plain.append(day);continue
        originals[n]=day
        clone={**day}
        for slot in _SLOT_KEYS:
            clone[slot]=[]
            for item in day.get(slot) or []:
                if isinstance(item,dict):
                    clone[slot].append(str(item.get('description') or ''))
                elif str(item).strip():clone[slot].append(str(item))
        plain.append(clone)
    cities=[d['city'] for d in topology(req)['days']]
    back=next((t for t in reversed(transports) if t.get('to')==req.departure_city),None)
    back_text=('按已确认班次'+str(back.get('name') or '')+'返回'+req.departure_city) if back else '按实际交通条件返程回到'+req.departure_city+'，具体班次和时刻待核实'
    normalized,fixes=_normalize_itinerary_days(plain,need,back_text,cities)
    canonical=ItineraryBody.model_validate({'days':normalized},context={'travel_days':need})
    result={'title':source.get('title') or '、'.join(req.destinations)+str(need)+'日行程','days':[]}
    for day in canonical.days:
        previous='00:00';original=originals.get(day.day,{})
        converted={'day':day.day,'city':day.city,'tips':day.tips}
        for slot in _SLOT_KEYS:
            items=[];old=original.get(slot) or []
            for i,text in enumerate(getattr(day,slot)):
                item=deepcopy(old[i]) if i<len(old) and isinstance(old[i],dict) else None
                if item is not None:
                    old_text=str(item.get('description') or '').strip()
                    if old_text!=text:fixes.append(f'第{day.day}天{_SLOT_LABELS[slot]}第{i+1}条补足原文60字约束')
                    item['description']=text
                    previous=item.get('end_time') or previous
                else:
                    provided=i<len(old) and isinstance(old[i],str) and bool(old[i].strip())
                    item={'name':'行程安排（时刻待确认）' if provided else '通用补位安排（待确认）','kind':'free','description':text,'start_time':previous,'end_time':previous,'source_ids':[]}
                    if provided:items.append(item);continue
                    fixes.append(f'第{day.day}天{_SLOT_LABELS[slot]}第{i+1}条为代码补位，不是已核实景点或实时报价')
                items.append(item)
            converted[slot]=items
        result['days'].append(converted)
    return result,canonical.model_dump(),list(dict.fromkeys(fixes))
