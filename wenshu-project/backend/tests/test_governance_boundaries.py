import pytest
from app.harness.base import Answer,VerificationResult,Intent

@pytest.mark.asyncio
async def test_rejected_answer_rewritten_twice_then_returns_only_quotes(fresh_container,monkeypatch):
 c=fresh_container
 await c.store.upsert_department({'_id':'dept_jwc','name':'教务处'})
 await c.store.insert_document({'_id':'d','title':'选课','dept_id':'dept_jwc','status':'active'})
 chunk={'_id':'d:0','doc_id':'d','dept_id':'dept_jwc','chunk_index':0,'content':'退课截止第八周','section_path':[]}
 await c.store.insert_chunks([chunk]);calls={'generate':0,'verify':0}
 async def retrieve(*a,**k):return [chunk]
 async def generate(*a,**k):calls['generate']+=1;return Answer(content='虚构：允许第999周退课',dept_ids=['dept_jwc'])
 async def verify(*a,**k):calls['verify']+=1;return VerificationResult(False,0,['无依据'])
 monkeypatch.setattr(c.retrieval_agent,'retrieve',retrieve);monkeypatch.setattr(c.orchestrator.answer_agent,'generate',generate);monkeypatch.setattr(c.orchestrator.verifier_agent,'verify',verify)
 result=await c.orchestrator.answer('退课截止时间',user_id='u',dept_ids=['dept_jwc'])
 assert calls=={'generate':3,'verify':3}
 assert '999' not in result['answer']and '第八周'in result['answer']
 assert result['verification']['passed']is False and result['verification']['degraded_to_quotes']

@pytest.mark.asyncio
async def test_feedback_cannot_mutate_active_skill_before_review(fresh_container,monkeypatch):
 c=fresh_container;monkeypatch.setattr(c.settings,'loop_phase','human_in_loop')
 await c.store.upsert_skill({'_id':'skill_dept_jwc_seed','status':'active','rubric_rules':[]})
 await c.loop_engine._adapt({'suggestions':[{'type':'rule','detail':'新增格式要求','dept_id':'dept_jwc'}]},[])
 assert(await c.store.get_skill('skill_dept_jwc_seed'))['rubric_rules']==[]
 assert(await c.store.find('rules'))[0]['status']=='pending'

@pytest.mark.asyncio
async def test_deploy_never_bypasses_failed_sandbox(fresh_container,monkeypatch):
 c=fresh_container;monkeypatch.setattr(c.settings,'loop_phase','human_out_of_loop')
 await c.store.upsert_skill({'_id':'candidate','status':'pending','auto_generated':True,'confidence':.99,'replay':{'passed':False,'candidate_score':0.0}})
 await c.loop_engine._deploy()
 assert(await c.store.get_skill('candidate'))['status']=='pending'

@pytest.mark.asyncio
async def test_replayed_feedback_is_idempotent(fresh_container):
 import asyncio
 c=fresh_container
 rows=await asyncio.gather(*[c.feedback_collector.collect_explicit('s','u','q','a','down')for _ in range(10)])
 assert sum(r['created']for r in rows)==1
 assert await c.store.count('feedback')==1
