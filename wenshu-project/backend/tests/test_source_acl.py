from datetime import datetime,timezone,timedelta
import pytest
from app.memory.facts import document_readable
from app.memory.policy import parse_time

@pytest.mark.asyncio
async def test_org_memory_cannot_bind_chunk_from_another_document(fresh_container):
 c=fresh_container
 await c.store.insert_document({'_id':'public','dept_id':'a','status':'active','version':'1'})
 await c.store.insert_document({'_id':'private','dept_id':'a','status':'active','version':'1','access_roles':['admin']})
 await c.store.insert_chunks([{'_id':'secret','doc_id':'private','content':'名单'}])
 with pytest.raises(ValueError):await c.organization_memory.publish('department','faq','事项','答案',[{'doc_id':'public','chunk_id':'secret'}],dept_id='a')

@pytest.mark.asyncio
async def test_org_memory_cannot_promote_private_sources_to_student(fresh_container):
 c=fresh_container
 await c.store.insert_document({'_id':'private','dept_id':'a','status':'active','version':'1','access_roles':['admin']})
 await c.store.insert_chunks([{'_id':'secret','doc_id':'private','content':'名单'}])
 await c.organization_memory.publish('department','faq','名单','名单信息',[{'doc_id':'private','chunk_id':'secret','document_version':'1'}],dept_id='a')
 assert await c.organization_memory.recall('名单',['a'],'student')==[]
 assert len(await c.organization_memory.recall('名单',['a'],'admin'))==1

def test_date_only_expiry_is_timezone_aware_and_enforced():
 assert parse_time('2026-01-01').tzinfo is not None
 assert not document_readable({'status':'active','expiry_date':'2001-01-01'})
 assert not document_readable({'status':'active','effective_date':'2099-01-01'})
