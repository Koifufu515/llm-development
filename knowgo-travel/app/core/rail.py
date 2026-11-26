"""交通事实的确定性边界：已确认路线、查询窗口、结构化结果与有界候选。"""
import hashlib
import json
import re
from datetime import date, timedelta

ALIASES = {"trainDate":"date", "departureDate":"date", "from":"fromStation", "fromCity":"fromStation", "to":"toStation", "toCity":"toStation"}


def normalize_query(parameters: dict, requirement: dict, today: date) -> dict:
    normalized = {}
    for key, value in parameters.items():
        target = ALIASES.get(key, key)
        if target not in {"date", "fromStation", "toStation"}:
            raise ValueError("包含不支持的查询参数")
        normalized[target] = value
    authoritative = {"date":requirement.get("departure_date"), "fromStation":requirement.get("departure_city"), "toStation":requirement.get("destination")}
    normalized.update({key:value for key,value in authoritative.items() if value})
    if any(not normalized.get(key) for key in authoritative):
        raise ValueError("缺少出发地、目的地或日期，请先补齐需求")
    target = date.fromisoformat(normalized["date"])
    if target < today:
        raise ValueError("日期已过去，请修改需求并重新确认，不能自动替换日期")
    if target > today + timedelta(days=14):
        raise ValueError("日期超出当前15天（含当天）的余票查询窗口，不能将未开售当作无车")
    if normalized['fromStation'] == normalized['toStation']:
        raise ValueError("出发地与目的地相同，是本地游，无需查询城际车票")
    return normalized


def content_text(content) -> str:
    if isinstance(content, str):return content
    if isinstance(content, list):return '\n'.join(block.get('text','') for block in content if isinstance(block,dict) and block.get('type')=='text')
    raise ValueError("不支持的MCP返回格式")


def compact_tickets(content, query: dict, limit: int = 12) -> dict:
    text = content_text(content)
    rows = json.loads(text)
    if not isinstance(rows,list):raise ValueError("返回值不是车次数组")
    rows = sorted(rows, key=lambda row: row.get('start_time','99:99'))
    options=[]
    for row in rows[:limit]:
        code=row['start_train_code']
        if not re.fullmatch(r'[A-Z]?\d+',code):raise ValueError("车次格式异常")
        if row.get('start_date') != query['date']:raise ValueError("车次日期与请求日期不一致")
        seats=[]
        for price in sorted(row.get('prices',[]),key=lambda p:{'二等座':0,'硬座':1,'一等座':2}.get(p.get('seat_name'),3))[:3]:
            value=price.get('price')
            seats.append({'name':price.get('seat_name'), 'availability':price.get('num'), 'price_yuan':value if isinstance(value,(int,float)) and not isinstance(value,bool) and value>=0 else None})
        key='|'.join([query['date'],code,row['start_time'],row['from_station_telecode'],row['to_station_telecode']])
        options.append({'option_id':hashlib.sha256(key.encode()).hexdigest()[:20], 'train_code':code,
                        'from_station':row['from_station'], 'to_station':row['to_station'],
                        'departure_date':row['start_date'], 'departure_time':row['start_time'],
                        'arrival_date':row['arrive_date'], 'arrival_time':row['arrive_time'],
                        'duration':row['lishi'], 'seats':seats})
    return {'status':'ok' if options else 'empty', 'query':query, 'source':'12306 via Joooook/12306-mcp',
            'source_url':'https://kyfw.12306.cn/', 'options':options,
            'original_count':len(rows), 'shown_count':len(options), 'original_characters':len(text)}


def render_ticket_table(result: dict) -> str:
    if result.get('status') != 'ok':return result.get('message','本次没有查到可用车次结果，请更换路线或稍后重试。')
    q=result['query']
    lines=[f"{q['date']} {q['fromStation']} → {q['toStation']}（按发车时间展示前{result['shown_count']}条，共返回{result['original_count']}条）",'','| 车次 | 实际到发站 | 发车 | 到达 | 历时 | 席别 / 余票 / 单价 |','|---|---|---|---|---|---|']
    for row in result['options']:
        seats='；'.join(f"{seat['name']} / {seat['availability']} / {str(seat['price_yuan'])+'元' if seat['price_yuan'] is not None else '票价暂无'}" for seat in row['seats'])
        lines.append(f"| {row['train_code']} | {row['from_station']} → {row['to_station']} | {row['departure_time']} | {row['arrival_date']} {row['arrival_time']} | {row['duration']} | {seats} |")
    lines+=['',f"来源：12306（经 Joooook/12306-mcp 查询）；查询时间：{result.get('queried_at','未记录')}。余票和票价可能变化。",'目前仅展示查询结果，尚未选定车次。']
    return '\n'.join(lines)
