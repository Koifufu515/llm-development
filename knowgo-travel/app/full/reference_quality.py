from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from app.full.quality import QwenJudge

# 裁判上下文：INPUT=需求清单，ACTUAL_OUTPUT=行程正文
_PARAMS = [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]

# 完整性维度的"预算明细"判据按源料二选一
# 背景：预算明细只存在于**流式 Markdown 正文**里（summarize_budget_tool / _build_budget 拼接），
# 结构化清单 TravelItinerary 只有 title + itinerary_list，**没有预算字段**。
# 离线评测喂的是 Markdown 正文（含预算表）→ 判据成立；
# 在线质检喂的是 plan_to_text 生成的结构化清单（无预算）→ 判据恒不满足，会系统性扣分。
# 因此改为显式开关，而不是让裁判自己去揣摩"这段文本里有没有预算"（确定性优先）。
_BUDGET_CLAUSE = ("2) 正文末尾附有预算明细（交通/住宿/餐饮/门票等构成）。缺任一项即扣分。")  # ★ 离线：源料是含预算表的正文
_BUDGET_CLAUSE_NA = ("《本条不适用》当前待判内容为结构化行程清单，本身不含预算明细，"  # ★ 在线：源料是没有预算字段的清单
                     "因此不得因缺少预算而扣分；只需判断第 1 项（天数与上午/下午/晚上时段）是否完整。")


def build_original_itinerary_metrics(model,threshold: float = 0.5, require_budget: bool = True) -> list[GEval]:
    """构造三维度 GEval（每次新建实例，避免 DeepEval 内部状态串扰）

    require_budget：待判源料是否含预算明细
    - True（默认）：源料是模型输出的 Markdown 正文，含预算表 → 严格校验预算完整性（离线评测口径不变）
    - False：源料是 plan_to_text 产出的结构化清单，无预算字段 → 该条判据不适用，不扣分（在线质检）
    """
    judge = QwenJudge.create(model)  # ★ 每次都新建，避免 DeepEval 内部状态串扰
    # 时段口径与代码渲染对齐——正文由 _render_itinerary_body 渲染为
    # **上午/中午/下午/晚上** 四个时段 + 每天"小贴士"（schema 强制），旧判据只写三个时段，
    # 判官口径与产物不一致；末日晚上允许只有 1 条（返程），不得据此判为不完整
    completeness = ("判断行程正文是否完整：1) 每天都有『Day X』标题，且当天包含上午/中午/"
                    "下午/晚上四个时段（末日晚上可只含返程 1 条，不算缺项），"
                    "天数覆盖需求里的全部出行天数；"
                    + (_BUDGET_CLAUSE if require_budget else _BUDGET_CLAUSE_NA))  # ★ 一个开关切两版判据
    return [
        GEval(name="行程完整性",
              criteria=completeness,
              evaluation_params=_PARAMS, model=judge, threshold=threshold),
        GEval(name="需求匹配度",
              criteria=("对照需求清单判断行程是否匹配：目的地正确；每天行程数量与出行天数一致；"
                        "交通方式与需求一致；行程设计体现旅行风格；按人数与预算给出合理的"
                        "餐饮住宿档次。明显偏离即扣分。"),
              evaluation_params=_PARAMS, model=judge, threshold=threshold),
        GEval(name="真实性（无编造）",
              criteria=("判断行程中的景点、餐厅、门票价格是否真实可信：景点应为目的地真实存在"
                        "的知名景点；餐厅应为当地真实特色；门票价格应与常识一致（如灵隐寺约"
                        " 30 元），不应出现明显虚构的名称或离谱价格。发现编造嫌疑即扣分。"),
              evaluation_params=_PARAMS, model=judge, threshold=threshold),
    ]


def build_itinerary_metrics(model,threshold=.5,require_budget=True,stable_steps=True):
    metrics=build_original_itinerary_metrics(model,threshold,require_budget)
    if not stable_steps:return metrics
    # 保留原三项criteria和阈值；修复每次动态生成步骤导致的额外需求与案例外事实。
    steps=[
        ['提取需求中明确天数和目的地，核对Day标题及覆盖；不增加用户没要求的字段。',
         '逐日检查上午/中午/下午/晚上，末日晚上仅返程一条也完整，交通占用时段不必再塞景点。',
         '需要预算时检查交通/住宿/餐饮/门票构成；require_budget=False时绝不因缺预算扣分。'],
        ['逐条对照用户明确的目的地、天数、人数和交通方式，不臆造额外条件。',
         '预算是人均时，使用人均合计比较，不能把全体总费用同人均上限比较；核对显著偏离。',
         '风格可以组合，经济住宿不等于只允许低价餐饮；未被明确禁止的合理活动不凭主观喜好扣分。'],
        ['只检查输出实际出现的景点/餐厅名和票价，criteria里灵隐寺仅是举例，不要求行程包含它。',
         '区分具体实体事实与就近用餐等泛化建议；泛化建议不当作编造餐厅。',
         '对明显虚构的实体或明显离谱的价格扣分；不能把裁判自己新生成的地名和价格当作已证实证据。']]
    for metric,defined in zip(metrics,steps):metric.evaluation_steps=defined
    return metrics
