import json

from fastmcp import FastMCP

from app.mcp_core.servers.weather_data import query_weather, resolve_city, safely_query

mcp = FastMCP("knowgo-weather")


@mcp.tool()
async def get_city_location(city: str) -> str:
    """查询中国城市的真实经纬度与省份。city 使用规范中文城市名，如杭州、苏州、上海。不是景点或路线查询。"""
    return json.dumps(await safely_query(resolve_city, city), ensure_ascii=False)


@mcp.tool()
async def get_weather_forecast(city: str, date: str | None = None) -> str:
    """查询中国城市近期真实天气预报。city 是城市名；date 是可选 YYYY-MM-DD。

    不传 date 返回当前7天预报；传 date 只查当天。超出窗口返回 date_out_of_range，
    此时不能用其他日期预报冒充。返回 source/queried_at/available_window 和气温、降水概率。
    """
    return json.dumps(await safely_query(query_weather, city, date), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
