"""原文4.7对照：仅本实验进程把分词放回事件循环，不改服务代码。"""
import asyncio,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarry.scripts import bench_async
original=asyncio.BaseEventLoop.run_in_executor

def inline(self,executor,func,*args):
 if getattr(func,'__name__','')!='build_tsquery':return original(self,executor,func,*args)
 fut=self.create_future()
 try:fut.set_result(func(*args))
 except Exception as e:fut.set_exception(e)
 return fut
asyncio.BaseEventLoop.run_in_executor=inline
if __name__=='__main__':asyncio.run(bench_async.main())
