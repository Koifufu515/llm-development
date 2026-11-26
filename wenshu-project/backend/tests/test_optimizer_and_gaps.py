import pytest
from app.storage.store import MemoryStore
from app.loop.optimizer import ParameterOptimizer
from app.loop.knowledge_gaps import KnowledgeGapManager
from app.loop.skill_executor import SkillExecutor

@pytest.mark.asyncio
async def test_bandit_uses_feedback_and_sticky_versioned_assignment():
 store=MemoryStore();optimizer=ParameterOptimizer(store)
 skill={'_id':'s','version':1,'status':'active','trigger':{'intent_patterns':['问']},'action':{'type':'workflow','steps':[{'action':'retrieve','params':{'top_k':5}}]},'parameter_experiment':{'enabled':True,'id':'p','arms':[{'id':'k3','top_k':3},{'id':'k5','top_k':5}]}}
 for arm,success in [('k3',True),('k5',False)]:
  for i in range(40):await store.upsert('strategy_executions',{'_id':arm+str(i),'artifact_id':'s','version':1,'parameter_experiment_id':'p','variant_id':arm,'success':success})
 chosen,assignment=await optimizer.choose(skill,'u','session')
 assert assignment['variant_id']=='k3'
 assert chosen['action']['steps'][0]['params']['top_k']==3
 assert (await optimizer.choose(skill,'u','session'))[1]==assignment
 assert skill['action']['steps'][0]['params']['top_k']==5

@pytest.mark.asyncio
async def test_selected_top_k_applies_below_default():
 store=MemoryStore();executor=SkillExecutor(store)
 skill={'_id':'s','version':1,'gray_percent':1,'trigger':{'intent_patterns':['问']},'action':{'type':'workflow','steps':[{'action':'retrieve','params':{'top_k':3}}]}}
 assert (await executor.prepare('问',['问'],[skill],'s','u')).top_k==3

@pytest.mark.asyncio
async def test_gap_workorder_is_idempotent_and_requires_official_active_source():
 store=MemoryStore();manager=KnowledgeGapManager(store)
 case={'_id':'fb','query':'材料如何办理','detail':{'dept_id':'a','root_cause':'knowledge_gap'}}
 ids=await manager.collect([case],{});assert ids
 assert await manager.collect([case],{})==ids
 assert await store.count('knowledge_workorders')==1
 with pytest.raises(ValueError):await manager.resolve(ids[0],'admin','a',['missing'],'已补充')
 await store.insert_document({'_id':'official','dept_id':'a','status':'active'})
 assert (await manager.resolve(ids[0],'admin','a',['official'],'已补充官方办法'))['status']=='resolved'
 with pytest.raises(PermissionError):await manager.resolve(ids[0],'other','b',['official'],'越权')
