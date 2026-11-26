"""版本隔离的Thompson Sampling；同一用户会话固定试验参数，反馈仅计一次。"""
from __future__ import annotations
import hashlib,random,copy
from datetime import datetime,timezone,timedelta
from app.loop.governance import validate_artifact

class ParameterOptimizer:
 def __init__(self,store):self.store=store
 async def choose(self,skill,user_id,session_id):
  experiment=skill.get('parameter_experiment')or{}
  if not experiment.get('enabled'):return skill,None
  arms=experiment.get('arms')or[{'id':'k3','top_k':3},{'id':'k5','top_k':5}]
  if not 2<=len(arms)<=8:raise ValueError('参数试验须包含2至8个候选')
  if len({a['id']for a in arms})!=len(arms):raise ValueError('参数臂ID必须唯一')
  for arm in arms:
   if set(arm)-{'id','top_k'}or type(arm.get('top_k'))is not int or not 1<=arm['top_k']<=20:raise ValueError('自动参数试验只能修改已声明的top_k')
  exp_id=experiment.get('id')or f"params:{skill['_id']}:{skill.get('version',1)}"
  signature=f"{exp_id}:{user_id}:{session_id}"
  assignment_id=hashlib.sha256(signature.encode()).hexdigest()
  assignment=await self.store.get('parameter_assignments',assignment_id)
  if not assignment:
   rows=await self.store.find('strategy_executions',{'artifact_id':skill['_id']})
   rows=[r for r in rows if r.get('parameter_experiment_id')==exp_id and r.get('version')==skill.get('version',1) and r.get('success')is not None]
   rng=random.Random(assignment_id);posterior={}
   for arm in arms:
    observed=[r for r in rows if r.get('variant_id')==arm['id']]
    successes=sum(r['success']is True for r in observed)
    alpha=1+successes;beta=1+len(observed)-successes
    posterior[arm['id']]={'alpha':alpha,'beta':beta,'sample':rng.betavariate(alpha,beta)}
   chosen=max(arms,key=lambda a:posterior[a['id']]['sample'])
   assignment=await self.store.create_once('parameter_assignments',{'_id':assignment_id,'experiment_id':exp_id,'variant_id':chosen['id'],'posterior':posterior,'created_at':datetime.now(timezone.utc)})
  chosen=next(a for a in arms if a['id']==assignment['variant_id'])
  candidate=copy.deepcopy(skill)
  for step in candidate.get('action',{}).get('steps',[]):
   if step.get('action')=='retrieve':step.setdefault('params',{})['top_k']=chosen['top_k']
  validate_artifact('skill',candidate)
  return candidate,{'variant_id':chosen['id'],'parameter_experiment_id':exp_id,'assignment_id':assignment_id}

class TriggerOptimizer:
 """依据版本内执行结果与显式漏触发标注生成候选；不把代理成功率称为人工准确率。"""
 def __init__(self,store):self.store=store
 async def propose(self,skill):
  rows=await self.store.find('strategy_executions',{'artifact_id':skill['_id']})
  cutoff=datetime.now(timezone.utc)-timedelta(days=7);observed=[]
  for row in rows:
   try:
    dt=datetime.fromisoformat(str(row.get('created_at','')).replace('Z','+00:00'))
    if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
   except ValueError:continue
   if dt>=cutoff and row.get('version')==skill.get('version',1) and row.get('group')=='treatment' and row.get('success')is not None:observed.append(row)
  feedback=await self.store.find('feedback');missed=[f for f in feedback if (f.get('detail')or{}).get('missed_skill_id')==skill['_id']]
  candidate=copy.deepcopy(skill);trigger=candidate.setdefault('trigger',{});changed=False
  if len(observed)>=10:
   success=sum(r['success']is True for r in observed)/len(observed)
   if success<.8:
    old=float(trigger.get('confidence_threshold',.75));trigger['confidence_threshold']=min(.95,old+.05);changed=trigger['confidence_threshold']!=old
  for f in missed:
   for pattern in (f.get('detail')or{}).get('suggested_intent_patterns',[])[:5]:
    if isinstance(pattern,str) and 1<len(pattern)<=30 and pattern not in trigger.get('intent_patterns',[]):trigger.setdefault('intent_patterns',[]).append(pattern);changed=True
  if not changed:return None
  import uuid
  candidate.update(_id='skill_tune_'+uuid.uuid4().hex,replaces=skill['_id'],version=int(skill.get('version',1))+1,status='pending',auto_generated=True,created_by='loop_trigger_optimizer',created_at=datetime.now(timezone.utc).isoformat())
  candidate['optimization_evidence']={'window_days':7,'completed_executions':len(observed),'explicit_miss_feedback_ids':[f['_id'] for f in missed],'measure':'执行成功率代理；漏触发由显式反馈标注，不是独立人工Precision/Recall'}
  validate_artifact('skill',candidate);return candidate
