"""导入有许可的历史景点描述；不导入旧餐厅、酒店、价格或营业时间。"""
import csv,json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote
from app.config import PROJECT_ROOT
NAMES=dict(zip(['Beijing','Shanghai','Suzhou','Nanjing','Hangzhou','Chengdu','Chongqing','Guangzhou','Shenzhen',"Xi'an",'Tianjin','Wuhan','Xiamen','Qingdao','Kunming','Dali','Lijiang','Guilin','Sanya','Fuzhou','Ningbo','Luoyang','Dunhuang','Huangshan','Changsha','Harbin','Dalian','Qufu','Taiyuan','Lhasa','Urumqi','Lanzhou','Jinan','Shenyang','Zhengzhou','Yangzhou','Wuxi','Zhuhai','Foshan','Quanzhou'],['北京','上海','苏州','南京','杭州','成都','重庆','广州','深圳','西安','天津','武汉','厦门','青岛','昆明','大理','丽江','桂林','三亚','福州','宁波','洛阳','敦煌','黄山','长沙','哈尔滨','大连','曲阜','太原','拉萨','乌鲁木齐','兰州','济南','沈阳','郑州','扬州','无锡','珠海','佛山','泉州']))
def main():
 source=PROJECT_ROOT/'data/full_sources/wikivoyage-listings-en.csv';root=PROJECT_ROOT/'data/full_guides';root.mkdir(exist_ok=True)
 groups=collections.defaultdict(list);seen=set()
 with source.open() as f:
  for row in csv.DictReader(f):
   prefix=row['article'].split('/')[0]
   if prefix not in NAMES or row['type'] not in ('see','do') or len(row['description'])<60:continue
   fingerprint=hashlib.sha256((row['title']+row['description']).encode()).hexdigest()
   if fingerprint in seen:continue
   seen.add(fingerprint);groups[row['article']].append(row)
 stamp=datetime.now(timezone.utc).isoformat();count=0
 for article,rows in groups.items():
  city=NAMES[article.split('/')[0]];url='https://en.wikivoyage.org/wiki/'+quote(article)
  paragraphs=['资料城市：'+city+'。本文是历史开放景点资料，不提供实时开放时间或价格；出行前需要核实。']
  for r in rows:paragraphs.append(r['title']+'\n'+r['description']);count+=1
  text='\n\n'.join(paragraphs)
  doc={'city':city,'title':city+'景点资料 · '+article,'source_url':url,'text':text,'retrieved_at':stamp,'license':'CC BY-SA 3.0','attribution':'Wikivoyage contributors; '+url,'sha256':hashlib.sha256(text.encode()).hexdigest(),'freshness':'历史数据快照，已知lastEdit至2016；采集时间不等于更新时间。仅作景点背景参考，出行细节需向官方核实。','poi_count':len(rows),'source_dataset':'https://github.com/wikivoyage/wikivoyage.github.io','excluded_fields':['price','hours','phone','email','hotel','restaurant']}
  (root/('wv-'+hashlib.sha256(article.encode()).hexdigest()[:16]+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2))
 report={'documents':len(groups),'cities':len({NAMES[a.split('/')[0]] for a in groups}),'poi_descriptions':count,'raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'freshness':'历史景点背景资料，不是现时营业数据'}
 (root/'import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
