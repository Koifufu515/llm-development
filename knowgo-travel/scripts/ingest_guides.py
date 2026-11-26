"""下载CC BY-SA旅行攻略正文，保留来源和版本；不将价格当实时事实。"""
import asyncio,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
import httpx
from bs4 import BeautifulSoup
from app.config import PROJECT_ROOT

CITIES=['北京','上海','天津','杭州','苏州','南京','西安','成都','重庆','广州','深圳','厦门','福州','武汉','长沙','青岛','济南','大连','沈阳','哈尔滨','长春','昆明','大理','丽江','桂林','南宁','贵阳','海口','三亚','郑州','洛阳','太原','兰州','银川','西宁','乌鲁木齐','拉萨','合肥','南昌','宁波','无锡','扬州','黄山','泉州','汕头','珠海','佛山','绍兴','嘉兴','湖州']

async def main():
    root=PROJECT_ROOT/'data/full_guides';root.mkdir(parents=True,exist_ok=True)
    sem=asyncio.Semaphore(3);report=[]
    async with httpx.AsyncClient(timeout=50,follow_redirects=True,headers={'User-Agent':'KnowgoTravelLearning/1.0 (local educational RAG; source attribution retained)'}) as client:
        async def fetch(city):
            target=root/(city+'.json')
            if target.exists():report.append({'city':city,'status':'cached'});return
            url='https://zh.wikivoyage.org/zh-hans/'+quote(city)
            async with sem:
                try:
                    response=await client.get(url);response.raise_for_status()
                    soup=BeautifulSoup(response.text,'html.parser')
                    content=soup.select_one('#mw-content-text .mw-parser-output') or soup.select_one('#mw-content-text')
                    if content is None:raise ValueError('没有攻略正文')
                    for bad in content.select('script,style,nav,.navbox,.toc,.mw-editsection,.metadata,.noprint,.sistersitebox,.thumb,.printfooter'):bad.decompose()
                    lines=[]
                    for element in content.find_all(['h2','h3','h4','p','li']):
                        if element.name=='li' and element.find_parent('li'):continue
                        value=re.sub(r'\s+',' ',element.get_text(' ',strip=True)).strip()
                        if len(value)>=12 and value not in lines:lines.append(value)
                    text='\n\n'.join(lines)
                    if len(text)<500:raise ValueError('正文不足500字符')
                    doc={'city':city,'title':city+'旅行指南','source_url':str(response.url),'text':text,
                         'retrieved_at':datetime.now(timezone.utc).isoformat(),'license':'CC BY-SA 4.0',
                         'attribution':'Wikivoyage contributors; '+url,'revision_history':url+'?action=history',
                         'sha256':hashlib.sha256(text.encode()).hexdigest(),
                         'freshness':'社区攻略，非实时行情；票价/开放时间/营业信息出行前需向官方核实'}
                    target.write_text(json.dumps(doc,ensure_ascii=False,indent=2))
                    report.append({'city':city,'status':'ok','characters':len(text),'source_url':str(response.url)})
                except Exception as exc:report.append({'city':city,'status':'failed','error':type(exc).__name__})
                print(json.dumps(report[-1],ensure_ascii=False),flush=True)
        await asyncio.gather(*(fetch(city) for city in CITIES))
    (root/'manifest.json').write_text(json.dumps({'documents':report,'downloaded_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2))

if __name__=='__main__':asyncio.run(main())
