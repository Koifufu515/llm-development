"""Open-Meteo 数据适配。HTTP 请求与 MCP 注册分开，便于验证日期和失败边界。"""
from datetime import date, datetime, timezone

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ALIASES = {
    "杭州": ("Hangzhou", "浙江"), "苏州": ("Suzhou", "江苏"), "宿州": ("Suzhou", "安徽"),
    "上海": ("Shanghai", "上海"), "北京": ("Beijing", "北京"), "南京": ("Nanjing", "江苏"),
    "深圳": ("Shenzhen", "广东"), "广州": ("Guangzhou", "广东"), "成都": ("Chengdu", "四川"),
    "武汉": ("Wuhan", "湖北"), "西安": ("Xi'an", "陕西"), "重庆": ("Chongqing", "重庆"),
    "天津": ("Tianjin", "天津"), "厦门": ("Xiamen", "福建"), "青岛": ("Qingdao", "山东"),
}


WMO_TEXT = {
    0: "晴", 1: "大部晴朗", 2: "多云", 3: "阴", 45: "雾", 48: "雾凇",
    51: "轻微毛毛雨", 53: "中等毛毛雨", 55: "强毛毛雨", 56: "轻微冻毛毛雨", 57: "强冻毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 66: "轻微冻雨", 67: "强冻雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "米雪", 80: "小阵雨", 81: "中阵雨", 82: "强阵雨",
    85: "小阵雪", 86: "强阵雪", 95: "雷暴", 96: "雷暴伴小冰雹", 99: "雷暴伴强冰雹",
}


def stamp() -> dict:
    return {"source": "Open-Meteo / GeoNames", "queried_at": datetime.now(timezone.utc).isoformat()}


def error(code: str, message: str, **extra) -> dict:
    return {"status": "unavailable", "code": code, "message": message, **stamp(), **extra}


async def resolve_city(client: httpx.AsyncClient, city: str) -> dict:
    city = city.strip()
    if not city or len(city) > 80:
        return error("invalid_city", "请提供明确的中国城市名称")
    normalized = city.removesuffix("市")
    query, province = ALIASES.get(normalized, (city, None))
    response = await client.get(GEOCODING_URL, params={"name": query, "count": 10, "language": "zh", "countryCode": "CN"})
    response.raise_for_status()
    candidates = response.json().get("results", [])
    if province:
        candidates = [c for c in candidates if province in c.get("admin1", "")]
    if not candidates:
        return error("city_not_found", "未找到城市，请补充省份或使用规范城市名")
    # 未配置别名的同名城市必须澄清，不直接把第一个结果当作用户所在地。
    if not province and len({(c.get("admin1"), c.get("name")) for c in candidates}) > 1:
        return error("ambiguous_city", "城市名称存在歧义，请明确省份与城市", candidates=[{"name":c.get("name"), "province":c.get("admin1")} for c in candidates[:5]])
    chosen = candidates[0]
    return {"status": "ok", "city": chosen["name"], "province": chosen.get("admin1"),
            "latitude": chosen["latitude"], "longitude": chosen["longitude"],
            "timezone": chosen.get("timezone", "Asia/Shanghai"), **stamp(), "source_url": GEOCODING_URL}


async def query_weather(client: httpx.AsyncClient, city: str, requested_date: str | None = None) -> dict:
    if requested_date:
        try:
            requested_date = date.fromisoformat(requested_date).isoformat()
        except ValueError:
            return error("invalid_date", "日期应为 YYYY-MM-DD，且必须是有效日期")
    place = await resolve_city(client, city)
    if place["status"] != "ok":
        return place
    response = await client.get(FORECAST_URL, params={
        "latitude": place["latitude"], "longitude": place["longitude"],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 7, "timezone": place["timezone"],
    })
    response.raise_for_status()
    payload = response.json()
    daily = payload["daily"]
    days = daily["time"]
    if not days:
        return error("empty_forecast", "数据源没有返回可用预报")
    window = {"start": days[0], "end": days[-1]}
    if requested_date and requested_date not in days:
        return error("date_out_of_range", "所选日期超出当前可查询预报窗口；暂不能提供当天预报", city=place["city"], requested_date=requested_date, available_window=window)
    rows = []
    for index, day in enumerate(days):
        if requested_date and day != requested_date:
            continue
        rows.append({"date": day, "weather_code": daily["weather_code"][index],
                     "weather_description": WMO_TEXT.get(daily["weather_code"][index], "未知天气代码"),
                     "temperature_max_c": daily["temperature_2m_max"][index],
                     "temperature_min_c": daily["temperature_2m_min"][index],
                     "rain_probability_percent": daily["precipitation_probability_max"][index]})
    return {"status": "ok", "city": place["city"], "province": place["province"],
            "timezone": place["timezone"], "available_window": window, "forecast": rows,
            "weather_code_standard": "WMO", **stamp(), "source_url": FORECAST_URL}


async def safely_query(operation, *args) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            return await operation(client, *args)
    except httpx.TimeoutException:
        return error("upstream_timeout", "天气或城市数据源超时，本次查询失败，请稍后重试")
    except httpx.HTTPError:
        return error("upstream_unavailable", "天气或城市数据源暂时不可用")
    except (KeyError, ValueError, IndexError, TypeError):
        return error("invalid_upstream_data", "数据源返回格式异常，未使用该结果")
