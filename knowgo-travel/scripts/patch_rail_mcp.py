"""12306-mcp 0.3.10：上车日期应来自本次查询，而不是列车始发日期。
原parseTicketsInfo以start_train_date构造日期，跨日运行到中间站时会少一天。
到达日仍用上车时间+区间历时计算；此补丁只改余票查询解析。
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'infra/rail-mcp/node_modules/12306-mcp/build/index.js'

def patched(source):
    if 'function parseTicketsInfo(ticketsData, map, boardingDate)' in source:return source
    changes=[('function parseTicketsInfo(ticketsData, map) {','function parseTicketsInfo(ticketsData, map, boardingDate) {'),
      ("const startDate = parse(ticket.start_train_date, 'yyyyMMdd', new Date());","const startDate = parse(boardingDate, 'yyyy-MM-dd', new Date());"),
      ('ticketsInfo = parseTicketsInfo(ticketsData, queryResponse.data.map);','ticketsInfo = parseTicketsInfo(ticketsData, queryResponse.data.map, date);')]
    for before,after in changes:
        if before not in source:raise ValueError('上游代码结构变化，停止自动补丁：'+before[:50])
        source=source.replace(before,after,1)
    return source

if __name__=='__main__':
    if not TARGET.exists():raise SystemExit('请先在infra/rail-mcp执行npm ci')
    source=TARGET.read_text();result=patched(source)
    if source!=result:TARGET.write_text(result)
    print('12306 MCP boarding-date patch ready')
