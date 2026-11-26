"""运行时 Skill 执行器：稳定灰度分桶并执行 workflow，而非仅拼接提示词。"""
from __future__ import annotations

import hashlib
import uuid
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.storage.store import DataStore
from app.loop.governance import workflow_steps


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SkillPlan:
    queries: list[str]
    top_k: int
    instructions: list[str] = field(default_factory=list)
    treatment_skills: list[dict[str, Any]] = field(default_factory=list)
    execution_ids: list[str] = field(default_factory=list)
    entities: dict[str, str] = field(default_factory=dict)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    missing_entities: list[str] = field(default_factory=list)


class SkillExecutor:
    def __init__(self, store: DataStore, default_top_k: int = 5) -> None:
        self.store = store
        self.default_top_k = default_top_k

    async def matching(self, query: str, dept_ids: list[str] | None = None, confidence: float = 1.0) -> list[dict[str, Any]]:
        skills = await self.store.list_skills(status="active")
        allowed = set(dept_ids or [])
        return [
            s for s in skills
            if (s.get("scope") == "global" or not allowed or s.get("dept_id") in allowed)
            and confidence >= float(s.get("trigger",{}).get("confidence_threshold",0))
            and not any(p and p in query for p in s.get("trigger",{}).get("negative_patterns",[]))
            and any(p and p in query for p in s.get("trigger", {}).get("intent_patterns", []))
        ]

    async def prepare(
        self, query: str, base_queries: list[str], skills: list[dict[str, Any]],
        session_id: str, user_id: str, entities: dict | None = None,
    ) -> SkillPlan:
        plan = SkillPlan(queries=list(base_queries), top_k=self.default_top_k, entities={"matter":query,**dict(entities or {})})
        for skill in skills:
            percent = float(skill.get("gray_percent", 1.0))
            percent = max(0.0, min(1.0, percent))
            bucket_key = f"{user_id}:{session_id}:{skill.get('_id')}:{skill.get('version', 1)}"
            bucket = int(hashlib.sha256(bucket_key.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
            group = "treatment" if bucket < percent else "control"
            execution_id = "strategy_exec_" + uuid.uuid4().hex
            await self.store.upsert("strategy_executions", {
                "_id": execution_id, "artifact_type": "skill", "artifact_id": skill.get("_id"),
                "version": skill.get("version", 1), "experiment_id": skill.get("experiment_id", ""),
                "group": group, "bucket": round(bucket, 6), "session_id": session_id,
                "user_id": user_id, "query": query, "success": None, "created_at": _now(),
            })
            plan.execution_ids.append(execution_id)
            if group == "control":
                continue
            from app.loop.optimizer import ParameterOptimizer
            skill, variant = await ParameterOptimizer(self.store).choose(skill,user_id,session_id)
            if variant:
                row = await self.store.get("strategy_executions",execution_id)
                row.update(variant)
                await self.store.upsert("strategy_executions",row)
            plan.treatment_skills.append(skill)
            self._execute_workflow(plan, skill, query)
            required = (skill.get("trigger") or {}).get("entities_required", (skill.get("trigger") or {}).get("required_entities",[]))
            plan.missing_entities = list(dict.fromkeys(plan.missing_entities+[key for key in required if not plan.entities.get(key)]))
            if not plan.missing_entities: await self.execute_tools(plan,skill)
        plan.queries = list(dict.fromkeys(q for q in plan.queries if q))
        return plan

    def _execute_workflow(self, plan: SkillPlan, skill: dict[str, Any], query: str) -> None:
        action = skill.get("action") or {}
        for step in workflow_steps(action):
            kind = step.get("action")
            params = step.get("params") or {}
            if kind == "extract_entity":
                entity = str(params.get("entity") or "matter")
                pattern = params.get("pattern")
                if pattern:
                    # 策略不可执行任意正则；仅提供限定的实体类型。
                    raise ValueError("工作流不接受动态正则代码")
                if entity == "matter":plan.entities[entity] = query
                elif entity == "grade":
                    match = re.search(r"(?:20\d{2}级|[一二三四五六]年级|[大研博][一二三四五])",query)
                    if match:plan.entities[entity] = match.group(0)
                elif entity == "semester":
                    match = re.search(r"(?:20\d{2}(?:[-—]20\d{2})?学年)?(?:[春秋]季(?:学期)?|[上下本这]学期)",query)
                    if match:plan.entities[entity] = match.group(0)
                elif entity == "degree":
                    match = re.search(r"本科生|研究生|博士生|硕士生",query)
                    if match:plan.entities[entity] = match.group(0)
            elif kind == "retrieve":
                template = str(params.get("query") or query)
                for key,value in {"matter":query,**plan.entities}.items():template=template.replace("{"+key+"}",str(value))
                plan.queries.append(template)
                plan.top_k = max(1,min(20,int(params.get("top_k",plan.top_k))))
            elif kind == "generate":
                template = params.get("template")
                if template and template != "default":
                    plan.instructions.append(f"使用输出模板：{template}")
            elif kind == "call_tool" and params.get("tool") == "calendar_lookup":
                plan.instructions.append("回答日期或截止时间时必须结合校历，并明确给出日期依据。")
        for rubric in skill.get("rubric_rules") or []:
            plan.instructions.append(str(rubric))

    async def execute_tools(self,plan: SkillPlan,skill: dict[str,Any]) -> None:
        for step in workflow_steps(skill.get("action")or{}):
            if step.get("action") != "call_tool":continue
            tool = (step.get("params") or {}).get("tool")
            if tool != "calendar_lookup":raise ValueError("未授权工作流工具")
            approval = await self.store.get("org_memory_items","orgmem_global_calendar")
            calendar = await self.store.get("global_memory","global")
            if approval and approval.get("status") == "active" and approval.get("review_status") == "approved":
                result = {"tool":tool,"data":(calendar or {}).get("calendar",{}),"authority":"admin_approved","source_refs":approval.get("source_refs",[])}
            else:
                result = {"tool":tool,"data":None,"error":"缺少已审核校历，不能推断日期"}
            plan.tool_results.append(result)
            plan.instructions.append("校历工具实际执行结果（日期须核对来源）："+json.dumps(result,ensure_ascii=False,default=str))

    async def record_outcome(self, execution_ids: list[str], success: bool, trace_id: str, latency_ms: int | None = None, model_usage: dict | None = None) -> None:
        for id_ in execution_ids:
            row = await self.store.get("strategy_executions", id_)
            if row:
                row.update({"success": bool(success), "verifier_success": bool(success), "trace_id": trace_id, "completed_at": _now()})
                row.update(latency_ms=latency_ms, model_usage=model_usage, cost_yuan=(model_usage or {}).get("cost_yuan"))
                await self.store.upsert("strategy_executions", row)
