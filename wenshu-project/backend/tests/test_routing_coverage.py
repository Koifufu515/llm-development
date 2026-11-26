import pytest
from app.storage.store import MemoryStore
from app.harness.agents.dept_router import DeptRouter

@pytest.mark.asyncio
async def test_generic_proposal_keyword_routes_to_actual_document_owner():
 store=MemoryStore()
 for id_,name in [('dept_yjsy','研究生院'),('dept_zfxy','中法学院')]:await store.upsert_department({'_id':id_,'name':name})
 await store.insert_document({'_id':'d','dept_id':'dept_zfxy','status':'active','title':'研究生开题报告通知','tags':['专业实践']})
 result=await DeptRouter(None,store).route('研究生开题报告字数要求是什么？')
 assert result['dept_ids']==['dept_zfxy'] and result['matched_by']=='keyword+knowledge_owner'

@pytest.mark.asyncio
async def test_private_document_does_not_influence_student_owner_route():
 store=MemoryStore();await store.upsert_department({'_id':'dept_zfxy','name':'中法学院'})
 await store.insert_document({'_id':'d','dept_id':'dept_zfxy','status':'active','title':'内部名单开题分组','access_roles':['admin']})
 class LLM:
  async def complete_json(self,*a,**kw):raise RuntimeError('not configured')
 result=await DeptRouter(LLM(),store).route('内部名单开题分组',user_role='student')
 assert result['matched_by']!='keyword+knowledge_owner'
