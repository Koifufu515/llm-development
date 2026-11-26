"""按2026-11-09百炼北京公开原价估算区间；不是实际账单扣费。"""
SOURCES={
 'qwen-plus':'https://help.aliyun.com/zh/model-studio/qwen-plus',
 'text-embedding-v4':'https://help.aliyun.com/zh/model-studio/text-embedding-v4',
 'qwen3-rerank':'https://help.aliyun.com/zh/model-studio/model-pricing',
}

def estimate(calls):
 low=high=0.;unknown=[]
 for call in calls:
  usage=call.get('usage');model=call.get('model')
  if not isinstance(usage,dict)or model not in SOURCES:
   unknown.append({'kind':call.get('kind'),'model':model,'reason':'缺少usage或未配置公开价格'});continue
  if model=='qwen-plus':
   input_tokens=usage.get('prompt_tokens')
   cache=int(usage.get('cacheRead',0)or(usage.get('prompt_tokens_details')or{}).get('cached_tokens',0)or 0)
   if input_tokens is None:input_tokens=int(usage.get('input',0))+cache+int(usage.get('cacheWrite',0))
   output=int(usage.get('completion_tokens',usage.get('output',0))or 0)
   if input_tokens<=128000:input_rate,out_low,out_high=.8,2,8
   elif input_tokens<=256000:input_rate,out_low,out_high=2.4,20,24
   else:input_rate,out_low,out_high=4.8,48,64
   # 上界不计输入缓存优惠，模式未明确记录时同时保留非思考/思考输出价格区间。
   low+=(max(0,input_tokens-cache)*input_rate+cache*input_rate*.2+output*out_low)/1e6
   high+=(input_tokens*input_rate+output*out_high+int(usage.get('cacheWrite',0))*.25*input_rate)/1e6
  else:
   tokens=usage.get('prompt_tokens',usage.get('input_tokens',usage.get('total_tokens')))
   if tokens is None:unknown.append({'kind':call.get('kind'),'model':model,'reason':'缺少输入Token数量'});continue
   low+=float(tokens)*.5/1e6;high+=float(tokens)*.5/1e6
 return {'currency':'CNY','lower_yuan':round(low,8),'upper_yuan':round(high,8),'complete':not unknown,'unknown_calls':unknown,'price_date':'2026-11-09','region':'百炼北京','billing_cost_yuan':None,'basis':'实际返回的usage×公开原价，区分缓存及未知思考模式；未计免费额度/活动/合同优惠，非实际账单','sources':SOURCES}
