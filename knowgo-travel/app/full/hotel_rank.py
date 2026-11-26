"""原文0289-9ca2b2b0a1c1共享酒店排序键。"""
_MIN_HOTEL_PRICE=25.0
def hotel_rank(price: float, score: float) -> tuple:
    """门店择优排序键（越小越优，供 min 代选）：异常低价排最后；评分≥4.5 按价格升序；
    评分<4.5 按评分降序、同分取更便宜（用负分折算成升序键）。

    状态机自动代选（hotel_flow.auto_select_hotels）与快速通道（express._pick_hotel）共用本函数，
    保证同一批候选在两通道选出同一家门店——此前状态机取首条、快速通道择优选，会漂移。
    """
    if float(price) < _MIN_HOTEL_PRICE:
        return (2, float("inf"), 0.0)
    if float(score) >= 4.5:
        return (0, float(price), 0.0)
    return (1, -float(score), float(price))
