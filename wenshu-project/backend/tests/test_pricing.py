from app.llm.pricing import estimate

def test_public_price_range_preserves_unknown_actual_bill():
 r=estimate([{'model':'qwen-plus','usage':{'input':1000,'output':100,'cacheRead':0}}, {'model':'qwen3-rerank','usage':{'total_tokens':2000}}])
 assert r['complete']and r['lower_yuan']==.002 and r['upper_yuan']==.0026
 assert r['billing_cost_yuan']is None

def test_unknown_model_or_usage_does_not_become_zero_bill():
 r=estimate([{'model':'other','usage':None}])
 assert not r['complete'] and len(r['unknown_calls'])==1 and r['billing_cost_yuan']is None
