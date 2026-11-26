import asyncio,json,hashlib,time,statistics
from pathlib import Path
from app.main import app
CASES=[('成都','成都大熊猫繁育研究基地有哪些值得看的内容？','Chengdu Panda Research Base of Giant Panda Breeding'),('广州','广州陈家祠有什么建筑特色？','Chen Clan Academy'),('深圳','深圳世界之窗主要能看什么？','Window of The World'),('青岛','青岛栈桥有哪些看点？','Zhan Qiao'),('大理','大理三塔有什么历史与游览特点？','Tang Dynasty Three Pagodas'),('哈尔滨','哈尔滨圣索菲亚教堂有什么特点？','St. Sophia Cathedral'),('敦煌','敦煌莫高窟有哪些文化看点？','Mogao Caves'),('拉萨','拉萨布达拉宫有什么历史特点？','Potala Palace'),('泉州','泉州开元寺值得看什么？','Kaiyuan Temple'),('太原','太原晋祠有什么历史看点？','Jinci Temple'),('兰州','兰州白塔山有哪些景观？','White Pagoda Mountain'),('无锡','无锡鼋头渚适合看哪些景色？',"Taihu Lake Yuantouzhu (Turtle's Head) Scenic Area"),('济南','济南趵突泉有什么特色？','Baotu Springs'),('洛阳','洛阳龙门石窟有哪些看点？','Longmen Grottoe'),('丽江','丽江黑龙潭可以欣赏什么？','Black Dragon Pool'),('三亚','三亚天涯海角有什么景观？','Tianya Haijiao'),('扬州','扬州瘦西湖有哪些特色？','Slender West Lake'),('长沙','长沙岳麓山有什么值得游览的？','Yuelu Mountain')]
async def main():
 async with app.router.lifespan_context(app):
  s=app.state.full;dataset=[]
  for city,q,name in CASES:
   gold=[p['id'] for p in s.knowledge.parents.values() if p['city']==city and name.lower() in p['text'].lower()]
   if not gold:raise ValueError('gold missing '+city)
   dataset.append({'city':city,'query':q,'target_name_in_source':name,'relevant_parent_ids':gold})
  frozen=json.dumps(dataset,ensure_ascii=False,sort_keys=True);digest=hashlib.sha256(frozen.encode()).hexdigest();Path('reports/full_rag_validation_set.json').write_text(json.dumps({'scope':'18城冻结验证集，与先前6城开发诊断分离；助手按原文实体标注，未经过用户人工审阅；仅评实体检索，不是问答准确率。','sha256':digest,'cases':dataset},ensure_ascii=False,indent=2))
  rows=[]
  for config,strategy,rerank in [('rrf','none',False),('expanded_reranked','multiquery',True)]:
   for case in dataset:
    t=time.perf_counter();r=await s.knowledge.search(case['query'],case['city'],k=5,model=s.model,strategy=strategy,rerank=rerank,use_cache=False)
    ids=[v['id'] for v in r['results']];gold=set(case['relevant_parent_ids']);hits=[i+1 for i,v in enumerate(ids) if v in gold]
    rows.append({'config':config,'city':case['city'],'recall_at_5':len(set(ids)&gold)/len(gold),'mrr':1/min(hits) if hits else 0,'hit_at_5':bool(hits),'city_isolation':all(v['city']==case['city'] for v in r['results']),'seconds':round(time.perf_counter()-t,4),'returned_parent_ids':ids})
    Path('reports/full_rag_validation.json').write_text(json.dumps({'dataset_sha256':digest,'scope':'同一冻结18问；按来源实体所在父块标注，未按结果再调参；不能外推线上QA准确率。','results':rows},ensure_ascii=False,indent=2));print(config,case['city'],bool(hits),flush=True)
if __name__=='__main__':asyncio.run(main())
