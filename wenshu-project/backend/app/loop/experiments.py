"""版本隔离的灰度评估：Fisher精确检验、分阶段升流、劣化回滚。"""
from __future__ import annotations
from datetime import datetime,timezone
from typing import Any
from scipy.stats import fisher_exact

def now():return datetime.now(timezone.utc).isoformat()

class ExperimentManager:
 def __init__(self,store,min_samples=30,alpha=.05,rollback_margin=.1,stages=(.1,.25,.5,1.0),latency_ratio=1.3):
  self.store=store;self.minimum=min_samples;self.alpha=alpha;self.margin=rollback_margin
  self.stages=stages;self.latency_ratio=latency_ratio
 async def outcomes(self,experiment):
  all_experiments=await self.store.find('experiments',{'artifact_id':experiment['artifact_id']})
  legacy=len(all_experiments)==1
  rows=await self.store.find('strategy_executions',{'artifact_id':experiment['artifact_id']})
  return [r for r in rows if r.get('success')is not None and
   (r.get('experiment_id')==experiment['_id']and r.get('version',experiment.get('version'))==experiment.get('version')
    or legacy and not r.get('experiment_id')and not r.get('version'))]
 async def evaluate(self,experiment):
  rows=await self.outcomes(experiment);t=[r for r in rows if r.get('group')=='treatment'];c=[r for r in rows if r.get('group')=='control']
  if len(t)<self.minimum or len(c)<self.minimum:return 'insufficient_samples'
  ts=sum(bool(r['success'])for r in t);cs=sum(bool(r['success'])for r in c)
  tr=ts/len(t);cr=cs/len(c)
  p=float(fisher_exact([[ts,len(t)-ts],[cs,len(c)-cs]],alternative='greater').pvalue)
  experiment.update({'treatment_success':tr,'control_success':cr,'sample_count':len(rows),'p_value':p,'test':'one-sided Fisher exact','updated_at':now()})
  measured_t=[r['latency_ms']for r in t if r.get('latency_ms')is not None]
  measured_c=[r['latency_ms']for r in c if r.get('latency_ms')is not None]
  guard=bool(measured_t and measured_c)and sum(measured_t)/len(measured_t)<=self.latency_ratio*max(1,sum(measured_c)/len(measured_c))
  skill=await self.store.get_skill(experiment['artifact_id'])
  if tr+self.margin<cr:
   experiment['status']='rolled_back';experiment['rollback_reason']='treatment_underperformed_control'
   if skill:
    skill.update({'status':'deprecated','rollback_reason':experiment['rollback_reason']});await self.store.upsert_skill(skill)
   await self.store.upsert('experiments',experiment);return 'rolled_back'
  previous=int(experiment.get('last_look_samples',0))
  # 仅新增一批样本后做下一次检验；alpha-spending上界总和不超过alpha。
  if len(rows)<previous+2*self.minimum:
   await self.store.upsert('experiments',experiment);return 'waiting_new_batch'
  look=int(experiment.get('statistical_looks',0))+1;threshold=self.alpha/(look*(look+1))
  experiment.update({'last_look_samples':len(rows),'statistical_looks':look,'alpha_for_look':threshold,'latency_guard_passed':guard})
  if tr>cr and p<threshold and guard and skill:
   current=float(experiment.get('gray_percent',skill.get('gray_percent',.1)))
   next_stage=next((x for x in self.stages if x>current+1e-8),1.0)
   experiment.setdefault('rollout_history',[]).append({'from':current,'to':next_stage,'p_value':p,'alpha':threshold,'sample_count':len(rows),'at':now()})
   experiment.update({'gray_percent':next_stage,'status':'completed'if next_stage==1 else'running'})
   skill['gray_percent']=next_stage;await self.store.upsert_skill(skill)
   action='promoted'
  else:action='hold'
  await self.store.upsert('experiments',experiment);return action
