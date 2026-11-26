import pytest
from app.loop.experiments import ExperimentManager
from app.loop.feedback_collector import FeedbackCollector
from app.storage.store import MemoryStore

async def setup_case(t_success,c_success):
 s=MemoryStore();e={'_id':'e','artifact_id':'s','version':2,'status':'running','gray_percent':.1};await s.upsert('experiments',e)
 await s.upsert_skill({'_id':'s','status':'active','version':2,'gray_percent':.1})
 for group,n in [('treatment',t_success),('control',c_success)]:
  for i in range(40):await s.upsert('strategy_executions',{'_id':f'{group}-{i}','artifact_id':'s','version':2,'experiment_id':'e','group':group,'success':i<n,'latency_ms':100})
 return s,e

@pytest.mark.asyncio
async def test_significant_benefit_advances_one_stage():
 s,e=await setup_case(40,10);m=ExperimentManager(s,min_samples=20)
 assert await m.evaluate(e)=='promoted'
 assert(await s.get_skill('s'))['gray_percent']==.25
 assert await m.evaluate(e)=='waiting_new_batch'

@pytest.mark.asyncio
async def test_non_significant_change_does_not_promote():
 s,e=await setup_case(31,30);assert await ExperimentManager(s,min_samples=20).evaluate(e)=='hold'

@pytest.mark.asyncio
async def test_old_version_outcomes_never_enter_new_experiment():
 s,e=await setup_case(40,10)
 for r in await s.find('strategy_executions'):r['version']=1;await s.upsert('strategy_executions',r)
 assert await ExperimentManager(s,min_samples=20).evaluate(e)=='insufficient_samples'

@pytest.mark.asyncio
async def test_explicit_feedback_updates_outcome_not_sample_count():
 s=MemoryStore();await s.insert_trace({'_id':'t','session_id':'session','user_id':'u','query':'问','answer':'答'})
 await s.upsert('strategy_executions',{'_id':'x','trace_id':'t','success':True})
 f=FeedbackCollector(s);await f.collect_explicit('session','u','问','答','down')
 assert(await s.get('strategy_executions','x'))['success']is False
 await f.collect_explicit('session','u','问','答','up')
 assert(await s.get('strategy_executions','x'))['success']is True
 assert await s.count('strategy_executions')==1
