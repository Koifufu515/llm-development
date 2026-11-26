"""原StepConfig前置依赖在工具执行侧复核，不能靠提示词阻止跳步。"""
from app.full.domain import Requirement,STEPS

def check_dependencies(state,target):
    if target not in STEPS:raise ValueError('无效步骤')
    req=Requirement.model_validate(state.get('requirement') or {})
    if not req.destinations:raise ValueError('请先确定目的地')
    current=STEPS.index(state.get('current_step','requirement_collection'))
    if target in ('itinerary_generation','budget_summarization'):
        if current<4:raise ValueError('交通和住宿尚未确认，不能跳过前置阶段')
        if 'selected_transport' not in state or 'selected_hotels' not in state:raise ValueError('缺少已确认交通或住宿记录')
        if not (state.get('food_preferences') or req.food_preferences):raise ValueError('请先确定餐饮偏好')
    return req
