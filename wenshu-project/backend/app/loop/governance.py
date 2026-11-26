"""Mutable Scope：概率性候选只可进入声明过的策略域，不能改事实和执行边界。"""
from __future__ import annotations
from copy import deepcopy
from typing import Any

class PolicyViolation(ValueError):
    pass

ALLOWED_STEPS = {'extract_entity', 'retrieve', 'call_tool', 'generate'}
ALLOWED_TOOLS = {'calendar_lookup'}


def workflow_steps(action):
    kind=action.get("type")
    if kind=="workflow":return action.get("steps")or[]
    if kind=="prompt":return [{"action":"generate","params":{"template":action.get("prompt")or action.get("template")or""}}]
    if kind=="tool_call":return [{"action":"call_tool","params":{"tool":action.get("tool"),"args":action.get("args")or{}}}]
    raise PolicyViolation("未知Skill动作类型")


def validate_artifact(kind: str, item: dict[str, Any]) -> None:
    if kind not in {'skill','hook','rule'}:
        raise PolicyViolation('未知策略类型')
    if len(str(item)) > 32000:
        raise PolicyViolation('策略内容超出限制')
    if item.get('scope','department') not in {'department','global'}:
        raise PolicyViolation('非法策略范围')
    if kind in {'skill','hook'}:
        trigger = item.get('trigger') or {}
        patterns = trigger.get('intent_patterns', [])
        if not isinstance(patterns, list) or not patterns or len(patterns)>30 or any(not isinstance(p,str) or not p.strip() or len(p)>200 for p in patterns):
            raise PolicyViolation('触发词必须为1至30个非空短文本')
        action = item.get('action') or {}
        if kind == 'hook':
            if action.get('type') != 'cross_dept_retrieval':
                raise PolicyViolation('未声明的Hook动作')
        else:
            steps=workflow_steps(action)
            if not 1 <= len(steps) <= 12:
                raise PolicyViolation('Skill必须是1至12步的声明式工作流、Prompt或白名单工具')
            if action.get('type')=='prompt' and not (action.get('prompt')or action.get('template')):
                raise PolicyViolation('Prompt不能为空')
            for step in steps:
                if step.get('action') not in ALLOWED_STEPS:
                    raise PolicyViolation('未声明的工作流步骤')
                params = step.get('params') or {}
                if step['action'] == 'call_tool' and params.get('tool') not in ALLOWED_TOOLS:
                    raise PolicyViolation('工具不在白名单')
                if 'top_k' in params and (type(params['top_k']) is not int or not 1 <= params['top_k'] <= 20):
                    raise PolicyViolation('top_k必须在1至20之间')
    elif not isinstance(item.get('content'),str) or not item['content'].strip():
        raise PolicyViolation('规则正文不能为空')
    if 'priority' in item and (type(item['priority']) is not int or not 0 <= item['priority'] < 100):
        raise PolicyViolation('动态策略不能覆盖系统优先级100的硬约束')


def protected_body(kind: str, item: dict[str, Any]) -> Any:
    if kind == 'rule':
        return item.get('content')
    action = deepcopy(item.get('action') or {})
    if kind == 'skill':
        for step in action.get('steps') or []:
            params = step.get('params') or {}
            # 模板参数可调，但Prompt模板、工具名和工作流拓扑必须审核。
            step['params'] = {k:v for k,v in params.items() if k not in {'top_k','query'}}
    return {'action':action,'rubric_rules':item.get('rubric_rules') or []}


def may_auto_activate(kind: str, item: dict, baseline: dict | None, phase: str, threshold: float, minimum_score: float) -> bool:
    validate_artifact(kind,item)
    if phase == 'human_in_loop' or baseline is None or baseline.get('status') != 'active':
        return False
    if protected_body(kind,item) != protected_body(kind,baseline):
        return False
    replay = item.get('replay') or {}
    if not replay.get('passed') or replay.get('sample_count',0)<1 or replay.get('candidate_score',0)<minimum_score:
        return False
    return phase == 'human_out_of_loop' or item.get('confidence',0) >= threshold


def sandbox_eligible(item,minimum=.85):
    if not item.get("auto_generated"):return True
    replay=item.get("replay")or{}
    return bool(replay.get("passed")) and replay.get("sample_count",0)>0 and replay.get("candidate_score",0)>=minimum
