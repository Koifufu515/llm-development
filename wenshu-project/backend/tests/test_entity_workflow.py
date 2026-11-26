import pytest
from app.storage.store import MemoryStore
from app.loop.skill_executor import SkillExecutor

@pytest.mark.asyncio
async def test_skill_extracts_grade_semester_and_expands_query():
 skill={'_id':'s','gray_percent':1,'trigger':{'intent_patterns':['选课'],'required_entities':['grade','semester']},'action':{'type':'workflow','steps':[{'action':'extract_entity','params':{'entity':'grade'}},{'action':'extract_entity','params':{'entity':'semester'}},{'action':'retrieve','params':{'query':'{grade}{semester}选课'}}]}}
 p=await SkillExecutor(MemoryStore()).prepare('2025级秋季学期选课',['选课'],[skill],'s','u')
 assert not p.missing_entities
 assert p.entities['grade']=='2025级'
 assert '2025级秋季学期选课' in p.queries
 p=await SkillExecutor(MemoryStore()).prepare('选课',['选课'],[skill],'s2','u')
 assert set(p.missing_entities)=={'grade','semester'}
 p=await SkillExecutor(MemoryStore()).prepare('怎么选',['怎么选'],[skill],'s3','u',entities={'grade':'2025级','semester':'秋季学期'})
 assert not p.missing_entities

@pytest.mark.asyncio
async def test_lifecycle_counts_recent_versioned_executions_not_lifetime():
 from app.config import Settings
 from app.deps import build_container
 from datetime import datetime,timezone,timedelta
 c=build_container(Settings(storage_mode='memory',vector_backend='memory',embedding_provider='hash',embedding_dim=128,pi_agent_enabled=False))
 old=(datetime.now(timezone.utc)-timedelta(days=30)).isoformat()
 now=datetime.now(timezone.utc).isoformat()
 skill={'_id':'old','status':'active','created_at':old,'version':1,'trigger':{'intent_patterns':['旧']},'action':{'type':'prompt','prompt':'引用原文'},'metrics':{'trigger_count':9999,'success_rate':1}}
 await c.store.upsert_skill(skill)
 await c.store.upsert('strategy_executions',{'_id':'past','artifact_id':'old','version':1,'group':'treatment','created_at':old,'success':True})
 await c.loop_engine._maintain_skill_lifecycle()
 assert (await c.store.get('skills','old'))['status']=='stale'
 skill.update(_id='recent',status='active',metrics={'trigger_count':0})
 await c.store.upsert_skill(skill)
 for i in range(5):await c.store.upsert('strategy_executions',{'_id':'now'+str(i),'artifact_id':'recent','version':1,'group':'treatment','created_at':now,'success':True})
 await c.loop_engine._maintain_skill_lifecycle()
 assert (await c.store.get('skills','recent'))['status']=='active'

@pytest.mark.asyncio
async def test_skill_confidence_negative_examples_and_sandbox_gate():
 from app.loop.governance import sandbox_eligible
 from app.loop.skill_miner import SkillMiner
 from app.config import Settings
 s=MemoryStore();skill={'_id':'s','status':'active','trigger':{'intent_patterns':['选课'],'negative_patterns':['取消'],'confidence_threshold':.8},'action':{'type':'prompt','prompt':'引用原文'}}
 await s.upsert_skill(skill);e=SkillExecutor(s)
 assert not await e.matching('选课',confidence=.5)
 assert not await e.matching('取消选课',confidence=.9)
 assert await e.matching('选课',confidence=.9)
 candidate={**skill,'auto_generated':True,'replay':{'passed':True,'sample_count':20,'candidate_score':.28}}
 assert not sandbox_eligible(candidate)
 miner=SkillMiner(s);await miner.register(candidate)
 assert (await s.get_skill('s'))['status']=='sandbox_failed'

@pytest.mark.asyncio
async def test_trigger_optimizer_requires_evidence_and_never_mutates_active_skill():
 from app.loop.optimizer import TriggerOptimizer
 from datetime import datetime,timezone
 s=MemoryStore();skill={'_id':'s','status':'active','version':1,'trigger':{'intent_patterns':['选课'],'confidence_threshold':.75},'action':{'type':'prompt','prompt':'引用原文'}};o=TriggerOptimizer(s)
 assert await o.propose(skill) is None
 for i in range(10):await s.upsert('strategy_executions',{'_id':str(i),'artifact_id':'s','version':1,'group':'treatment','success':False,'created_at':datetime.now(timezone.utc).isoformat()})
 c=await o.propose(skill)
 assert c['trigger']['confidence_threshold']==.8 and c['status']=='pending'
 assert skill['trigger']['confidence_threshold']==.75
 await s.upsert('feedback',{'_id':'miss','detail':{'missed_skill_id':'s','suggested_intent_patterns':['退选']}})
 assert '退选' in (await o.propose(skill))['trigger']['intent_patterns']
