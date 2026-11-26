"""用户/部门固定窗口预算；Redis多副本原子检查，故障不静默失效。"""
import hashlib,time,asyncio

LUA='''
for i,key in ipairs(KEYS) do
 if tonumber(redis.call('GET',key) or '0') >= tonumber(ARGV[i+1]) then return 0 end
end
for _,key in ipairs(KEYS) do
 local count=redis.call('INCR',key)
 if count==1 then redis.call('EXPIRE',key,ARGV[1]) end
end
return 1
'''
class DistributedBudget:
 def __init__(self,sessions):self.sessions=sessions;self.local={};self.lock=asyncio.Lock()
 async def take(self,items,window=60):
  keys=['{wenshu_budget}:'+hashlib.sha256(f'{scope}:{identity}'.encode()).hexdigest()for scope,identity,limit in items]
  limits=[limit for scope,identity,limit in items]
  redis=getattr(self.sessions,'_redis',None)
  if hasattr(self.sessions,'_redis'):
   if redis is None:raise RuntimeError('Redis预算服务未就绪')
   return bool(await redis.eval(LUA,len(keys),*keys,window,*limits))
  async with self.lock:
   now=time.monotonic()
   for key,limit in zip(keys,limits):
    count,expiry=self.local.get(key,(0,0))
    if expiry>now and count>=limit:return False
   for key in keys:
    count,expiry=self.local.get(key,(0,0))
    self.local[key]=(count+1,expiry)if expiry>now else(1,now+window)
   return True
