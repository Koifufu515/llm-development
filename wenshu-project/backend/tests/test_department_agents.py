"""部门 Agent 隔离、并行部分成功和共享向量测试。"""
from __future__ import annotations

import asyncio

import pytest

from app.config import Settings
from app.integrations.dept_agent_client import DepartmentAgentClient
from app.retrieval.vector_store import MongoVectorStore
from app.storage.store import MemoryStore


@pytest.mark.asyncio
async def test_department_client_parallel_partial_success(monkeypatch):
    client = DepartmentAgentClient(Settings(dept_agents_enabled=True, dept_id=""))
    active = 0
    peak = 0

    async def fake(query, dept_id, session_id, user_id, memory_context=""):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        if dept_id == "dept_cwc":
            raise TimeoutError("timeout")
        return {"answer": dept_id, "dept_ids": [dept_id]}

    monkeypatch.setattr(client, "_answer_one", fake)
    results, failed = await client.answer_many(
        "休学退费", ["dept_jwc", "dept_cwc"], "s1", "u1", "上一轮事项：休学"
    )
    assert peak == 2
    assert results[0]["dept_ids"] == ["dept_jwc"]
    assert failed == ["dept_cwc"]


@pytest.mark.asyncio
async def test_orchestrator_enforces_dept_id(fresh_container):
    c = fresh_container
    c.settings.dept_id = "dept_jwc"
    with pytest.raises(PermissionError):
        await c.orchestrator.answer("学费", dept_ids=["dept_cwc"])


@pytest.mark.asyncio
async def test_mongo_vector_store_is_shared():
    store = MemoryStore()
    writer = MongoVectorStore(store)
    reader = MongoVectorStore(store)
    await writer.add("c1", [1.0, 0.0], {"doc_id": "d1", "dept_id": "dept_jwc"})
    hits = await reader.search([1.0, 0.0], dept_id="dept_jwc")
    assert hits and hits[0]["id"] == "c1"
    await reader.delete_by_doc("d1")
    assert await writer.count() == 0

def test_merged_citations_are_renumbered_and_verdict_not_fabricated():
 from app.harness.orchestrator import Orchestrator
 one={'answer':'事实[来源1]','dept_ids':['a'],'citations':[{'doc_id':'a','chunk_index':0}],'verification':{'passed':True}}
 two={'answer':'另一事实[来源1]','dept_ids':['b'],'citations':[{'doc_id':'b','chunk_index':0}],'verification':{'passed':False}}
 result=Orchestrator._merge_department_answers([one,two],[])
 assert '[来源2]'in result.content and len(result.citations)==2
 assert not result.verification['passed']

def test_department_url_cannot_escape_service_hostname():
 client=DepartmentAgentClient(Settings(dept_agents_enabled=True))
 for malicious in ['dept_attacker.example','dept_a/path','dept_x:8080','http://example.com']:
  with pytest.raises(ValueError):client.url(malicious)

@pytest.mark.asyncio
async def test_all_remote_failures_are_explicit_in_local_fallback(fresh_container):
 c=fresh_container
 c.orchestrator.settings=c.orchestrator.settings.model_copy(update={'dept_id':''})
 class Failed:
  enabled=True
  async def answer_many(self,*args,**kwargs):return [],['dept_hqaq']
 c.orchestrator.dept_agent_client=Failed()
 result=await c.orchestrator.answer('暴雨可以骑行吗',dept_ids=['dept_hqaq'])
 assert result['verification']['partial']
 assert result['verification']['degraded_departments']==['dept_hqaq']
 assert '共享制度检索回退' in result['answer']
