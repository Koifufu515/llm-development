from datetime import datetime,timezone,timedelta
import pytest
from app.storage.store import MemoryStore
from app.pipeline.lifecycle import DocumentLifecycle
from app.pipeline.glossary import GlossaryExtractor
from app.pipeline.conflict_workflow import ConflictWorkflow

@pytest.mark.asyncio
async def test_expiry_reminders_idempotent_and_history_kept():
 store=MemoryStore();now=datetime.now(timezone.utc)
 await store.insert_document({'_id':'old','dept_id':'a','title':'办法','status':'archived','created_at':'1'})
 await store.insert_document({'_id':'new','dept_id':'a','title':'办法','status':'active','created_at':'2','expiry_date':now+timedelta(days=1)})
 life=DocumentLifecycle(store,None)
 assert len(await life.remind_expiring(now))==1
 await life.remind_expiring(now)
 assert await store.count('notifications')==1
 assert [r['_id']for r in await life.history('new')]==['old','new']

@pytest.mark.asyncio
async def test_unready_document_cannot_be_activated():
 store=MemoryStore();await store.insert_document({'_id':'d','status':'review','vector_status':'failed'})
 with pytest.raises(ValueError):await DocumentLifecycle(store,None).transition('d','active','admin')

@pytest.mark.asyncio
async def test_terms_only_queryable_after_review():
 store=MemoryStore();doc={'_id':'d','dept_id':'a','status':'active'};await store.insert_document(doc)
 await store.insert_chunks([{'_id':'d:0','doc_id':'d','content':'研究生培养办公室（简称研培办）负责受理。'}])
 ex=GlossaryExtractor(store);rows=await ex.extract(doc);assert rows[0]['synonyms']==['研培办']
 assert not await store.find('glossary')
 await ex.review(rows[0]['_id'],'admin',True)
 assert len(await store.find('glossary'))==1

@pytest.mark.asyncio
async def test_conflict_requires_both_departments_confirmation():
 store=MemoryStore();wf=ConflictWorkflow(store)
 await wf.open({'_id':'r','relation_type':'conflict','from_dept':'a','to_dept':'b'})
 assert await store.count('notifications')==2
 with pytest.raises(PermissionError):await wf.advance('r','reviewing','c','c','核对')
 await wf.advance('r','reviewing','a','a','已核对两个版本')
 await wf.advance('r','coordinating','a','a','发起协调')
 assert (await wf.advance('r','resolved','a','a','接受统一口径'))['status']=='coordinating'
 assert (await wf.advance('r','resolved','b','b','接受统一口径'))['status']=='resolved'
 assert (await wf.advance('r','closed','a','a','新文档发布后关闭'))['status']=='closed'
