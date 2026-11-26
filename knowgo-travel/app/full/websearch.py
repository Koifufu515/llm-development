"""百炼联网搜索：摘要是检索结果，不冒充已读取网页或官方核实结论。"""
import hashlib,asyncio,json
from app.core.rail import content_text
from datetime import datetime,timezone
from urllib.parse import urlparse

async def search_web(services,city,query,count=3):
    pages=[];provider='Tavily'
    try:
        tools=services.mcp_manager.tools.get('search') or await services.mcp_manager.load_service('search')
        tool=next(t for t in tools if t.name=='search_travel_info')
        data=json.loads(content_text(await asyncio.wait_for(tool.ainvoke({'query':city+' '+query,'max_results':min(count,5)}),40)))
        pages=[{**r,'snippet':r.get('content','')} for r in data.get('results',[])]
    except Exception:pass
    if not pages:
        provider='百炼联网搜索'
        raw=await services.remote.query('search',('bailian_web_search',),{'query':city+' '+query,'count':min(count,5)})
        pages=raw.get('data',{}).get('pages',[]) if isinstance(raw.get('data'),dict) else []
    rows=[]
    for page in pages:
        url=page.get('url','');text=page.get('snippet','')
        if urlparse(url).scheme not in ('http','https') or len(text)<20:continue
        rows.append({'id':hashlib.sha256((city+url).encode()).hexdigest()[:24],'city':city,'title':page.get('title',city+'联网搜索'),
          'text':text[:2000],'source_url':url,'license':'外部搜索摘要，仅供引用溯源','retrieved_at':datetime.now(timezone.utc).isoformat(),
          'freshness':'联网搜索当次摘要；摘要可能过时或互相矛盾，出行前应核对景区官方公告。','source_type':'web_search','provider':provider})
    return {'status':'ok' if rows else 'unavailable','provider':provider,'results':rows,'notice':'联网搜索摘要，不等同官方网站核验；不从标题推断网站为官方。'}
