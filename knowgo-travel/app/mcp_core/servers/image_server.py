"""原方案图片检索能力的独立stdio MCP；私有geng端点缺失时使用已授权Tavily。
API依据 https://docs.tavily.com/documentation/api-reference/endpoint/search
只返回来源图片URL及说明，不下载或重托管第三方图片。
"""
import json
import httpx
from fastmcp import FastMCP
from app.config import Settings
mcp=FastMCP('knowgo-image-search')

@mcp.tool()
async def search_travel_images(query:str,max_results:int=5)->str:
    """联网检索具体旅游地点的图片，返回原图URL、可用描述与来源页；不保证授权或链接长期有效。"""
    key=Settings().tavily_api_key.get_secret_value().strip()
    if not key:return json.dumps({'status':'unavailable','message':'图片搜索未配置'},ensure_ascii=False)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.post('https://api.tavily.com/search',headers={'Authorization':'Bearer '+key},json={'query':query,'max_results':max(1,min(max_results,10)),'include_images':True,'include_image_descriptions':True,'include_answer':False})
        if response.status_code!=200:return json.dumps({'status':'unavailable','http_status':response.status_code})
        data=response.json();images=[]
        for row in data.get('images',[]):
            url=row.get('url') if isinstance(row,dict) else row
            if isinstance(url,str) and url.startswith(('https://','http://')):
                images.append({'url':url,'description':row.get('description','') if isinstance(row,dict) else ''})
        return json.dumps({'status':'ok' if images else 'empty','query':query,'source':'Tavily图片搜索','images':images[:max(1,min(max_results,10))],'source_pages':[{'title':r.get('title'),'url':r.get('url')} for r in data.get('results',[])]},ensure_ascii=False)
    except Exception as exc:return json.dumps({'status':'unavailable','error_type':type(exc).__name__})

if __name__=='__main__':mcp.run(transport='stdio',show_banner=False)
