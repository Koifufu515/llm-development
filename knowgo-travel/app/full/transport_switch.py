"""0619原文否定过滤/最后一个肯定方式优先；无模型调用。"""
import re
from typing import Any, Optional



_TRANSPORT_STEP = "transport_planning"

# 方式 → 用户可读名（改选回执、降级说明共用）
MODE_LABELS = {"train": "高铁", "flight": "航班", "driving": "自驾"}

# 口语词 → 方式。与三个 flow 的表单词表同口径，另补口语变体；命名分组识别方式
_MODE_RE = re.compile(
    r"(?P<train>高铁|动车|火车|铁路)"
    r"|(?P<flight>飞机|航班|机票|乘机|飞过去)"
    r"|(?P<driving>自驾|开车|驾车)"
)

# 前置否定：否定词后最多隔2个字就是方式词
_NEG_BEFORE = re.compile(
    r"(不坐|不乘|不搭|不要|不想|不用|不选|不订|不买|不开|不走|不考虑|"
    r"别坐|别乘|别订|别选|别开|放弃|取消|拒绝)[^，,。；;！!？?\s]{0,2}$"
)
# 后置否定：方式词后最多隔2个字出现否定
_NEG_AFTER = re.compile(
    r"^[^，,。；;！!？?\s]{0,2}(没有|没票|没了|不行|不要|不坐|算了|查不到|订不到|买不到|"
    r"不可用|不方便|不考虑|去不了|到不了|太贵|太慢|太累|太远|取消)"
)

# 卡片提交后的合成续跑发言以此开头，不属于用户手动改选
_SYNTH_PREFIXES = ("我已按卡片", "我已确认全部")

def detect_transport_switch(text: str, current: Optional[str] = None) -> Optional[str]:
    """从用户原话识别改选目标（纯函数，无IO）
    规则：
    - 方式词前后紧邻否定词视为不选择该方式；
    - 在肯定提及中取最后一个与当前方式不同的作为目标；
    - 仅重申当前方式、无方式提及则返回 None，不修改状态。
    """
    text = str(text or "").strip()
    if not text or text.startswith(_SYNTH_PREFIXES):
        return None
    positives: list[str] = []
    for m in _MODE_RE.finditer(text):
        before = text[max(0, m.start() - 6):m.start()]
        after = text[m.end():m.end() + 8]
        if _NEG_BEFORE.search(before) or _NEG_AFTER.search(after):
            continue
        positives.append(m.lastgroup)
    for mode in reversed(positives):
        if mode != current:
            return mode
    return None

