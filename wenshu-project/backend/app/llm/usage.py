"""请求局部模型账本：仅记服务端返回的usage，未知金额为null。"""
from contextvars import ContextVar
from functools import wraps
from copy import deepcopy

_calls = ContextVar('wenshu_model_calls', default=None)

def record(kind, model, usage, **metadata):
    calls=_calls.get()
    if calls is not None:
        calls.append({'kind':kind,'model':model,'usage':usage if isinstance(usage,dict) else None,**metadata})

def snapshot():
    calls=deepcopy(_calls.get() or [])
    from app.llm.pricing import estimate
    return {'calls':calls,'usage_complete':all(c.get('usage') is not None for c in calls),'cost_yuan':None,'estimated_cost':estimate(calls)}

def request_usage(fn):
    @wraps(fn)
    async def wrapped(*args,**kwargs):
        token=_calls.set([])
        try:
            result=await fn(*args,**kwargs)
            result['model_usage']=snapshot()
            return result
        finally:_calls.reset(token)
    return wrapped
