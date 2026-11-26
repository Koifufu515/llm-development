"""真实HTTP/Harness/数据库/Redis链路，模型为隔离延时fixture。"""
import asyncio,httpx,time,json,os,statistics,argparse
async def main(a):
 start=time.monotonic();latencies=[];statuses={};errors={};responses=0;cache_hits=0;min_calls=None;completions=[]
 timeout=httpx.Timeout(90);limits=httpx.Limits(max_connections=a.concurrency,max_keepalive_connections=0)
 async with httpx.AsyncClient(timeout=timeout,limits=limits)as client:
  async def worker(i):
   nonlocal responses,cache_hits,min_calls
   n=0
   while time.monotonic()-start<a.seconds:
    began=time.monotonic();n+=1
    try:
     r=await client.post(a.base+'/api/v1/internal/dept/answer',headers={'X-Internal-Token':os.environ['INTERNAL_API_TOKEN'],'Connection':'close'},json={'query':'压测事项要提交几份材料？','dept_id':'dept_load_fixture','session_id':f'load-{a.tag}-{i}-{n}','user_id':f'synthetic-user-{i}'})
     statuses[str(r.status_code)]=statuses.get(str(r.status_code),0)+1
     if r.status_code==200 and r.json().get('code')==0:
      data=r.json()['data'];calls=len((data.get('model_usage')or{}).get('calls',[]));min_calls=calls if min_calls is None else min(min_calls,calls)
      cache_hits+=bool(data.get('cache_hit'));responses+=1
      completions.append({'t':time.monotonic()-start,'latency':time.monotonic()-began})
     else:errors['http_error']=errors.get('http_error',0)+1
    except Exception as exc:errors[type(exc).__name__]=errors.get(type(exc).__name__,0)+1
    latencies.append(time.monotonic()-began)
  await asyncio.gather(*[worker(i)for i in range(a.concurrency)])
 duration=time.monotonic()-start;ordered=sorted(latencies)
 report={'tag':a.tag,'model':'synthetic fixture 3s answer delay, zero external model calls','concurrency':a.concurrency,'seconds':duration,'requests':len(latencies),'successful':responses,'throughput_rps':responses/duration,'statuses':statuses,'errors':errors,'p50_seconds':statistics.median(ordered)if ordered else None,'p95_seconds':ordered[min(len(ordered)-1,int(len(ordered)*.95))]if ordered else None}
 report.update(cache_mode='disabled',observed_cache_hits=cache_hits,minimum_model_calls_per_answer=min_calls)
 window=min(60,a.seconds);steady=[r for r in completions if a.seconds-window<=r['t']<=a.seconds]
 report['steady_last_window']={'seconds':window,'successful':len(steady),'throughput_rps':len(steady)/window,'p95_seconds':sorted(r['latency']for r in steady)[min(len(steady)-1,int(len(steady)*.95))]if steady else None}
 print(json.dumps(report),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',default='http://dept-agent-load-proof:8000');p.add_argument('--seconds',type=int,default=300);p.add_argument('--concurrency',type=int,default=180);p.add_argument('--tag',default='scale');asyncio.run(main(p.parse_args()))
