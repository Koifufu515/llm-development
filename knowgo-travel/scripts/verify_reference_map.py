"""修复真实浏览器发现的景点误匹配停车场，仅更新合成基准账号的地图展示，不改正文/预算/历史版本。"""
import asyncio,json,copy
from pathlib import Path
from app.main import app
from app.full.database import Plan
from app.full.plans import enrich_map,poi_matches
async def main():
    benchmark=json.loads(Path('reports/reference-flow-final.json').read_text());rows=[]
    async with app.router.lifespan_context(app):
        services=app.state.full
        # 独立实际高德查询验证景点本体，不靠旧照片或模型常识。
        probe={'days':[{'city':'苏州','day':1,'morning':[{'kind':'attraction','name':'苏州博物馆参观'}],'noon':[],'afternoon':[],'evening':[]}]}
        result=await enrich_map(services,probe)
        Path('reports/reference-map-probe.json').write_text(json.dumps({'scope':__doc__,'probe':result,'matched_main_attraction':any('博物馆' in p['name'] and '停车' not in p['name']for p in result['points'])},ensure_ascii=False,indent=2))
        # 仅清理已知合成验收行程的错误附属设施；对发现问题的计划重新查询地图。
        for trial in benchmark['rows']:
            if not trial.get('plan_id'):continue
            async with services.db.session() as db:
                plan=await db.get(Plan,trial['plan_id']);old=copy.deepcopy(plan.map_data)
                bad=[p for p in old.get('points',[])if not poi_matches(p.get('source_activity',''),p.get('name',''))]
                if not bad and plan.id!=next((t.get('plan_id') for t in benchmark['rows'] if t['mode']=='express' and t['repeat']==1),None):continue
                new=await enrich_map(services,plan.body);plan.map_data=new;await db.commit()
                rows.append({'plan_id':plan.id,'bad_before':[p['name']for p in bad],'points_after':[p['name']for p in new.get('points',[])],'no_auxiliary_mismatch':all(poi_matches(p['source_activity'],p['name'])for p in new.get('points',[]))})
        Path('reports/reference-map-fix.json').write_text(json.dumps({'scope':__doc__,'probe_matched':bool(result['points']),'repaired_synthetic_plans':rows},ensure_ascii=False,indent=2));print('probe',len(result['points']),'repaired',len(rows),flush=True)
asyncio.run(main())
