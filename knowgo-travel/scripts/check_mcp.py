"""独立验证 MCP 发现工具和真实调用，不调用 LLM。"""
import asyncio
import json
from pathlib import Path

from app.mcp_core.client import load_weather_tools


def decode(content):
    if isinstance(content, str):
        return json.loads(content)
    return json.loads(next(item["text"] for item in content if item.get("type") == "text"))


async def main():
    tools = {tool.name: tool for tool in await load_weather_tools()}
    print("MCP发现工具：", list(tools), flush=True)
    location = decode(await tools["get_city_location"].ainvoke({"city": "杭州"}))
    forecast = decode(await tools["get_weather_forecast"].ainvoke({"city": "杭州"}))
    unavailable = decode(await tools["get_weather_forecast"].ainvoke({"city": "杭州", "date": "2099-01-01"}))
    assert location["status"] == "ok", location
    assert forecast["status"] == "ok" and forecast["forecast"], forecast
    assert unavailable["code"] == "date_out_of_range" and "forecast" not in unavailable, unavailable
    report = {"transport": "stdio MCP", "tools": list(tools), "location": location, "forecast": forecast, "out_of_range": unavailable}
    Path("MCP真实验证.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
