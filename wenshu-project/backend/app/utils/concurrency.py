"""对进入完整Harness的请求背压；等待也计入部门HTTP在途指标。"""
import functools,time

def bounded_execution(fn):
 @functools.wraps(fn)
 async def wrapped(self,*args,**kwargs):
  start=time.monotonic()
  async with self._request_slots:
   waited=time.monotonic()-start
   result=await fn(self,*args,**kwargs)
   result['queue_wait_ms']=round(waited*1000,3)
   return result
 return wrapped
