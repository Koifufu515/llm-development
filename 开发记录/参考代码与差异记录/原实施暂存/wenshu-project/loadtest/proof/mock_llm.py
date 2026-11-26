"""仅用于隔离负载测试：本机合成模型，不计入真实Qwen性能。"""
import asyncio,json,os
from fastapi import FastAPI,Request
import uvicorn
app=FastAPI()
@app.post('/v1/chat/completions')
async def completion(request:Request):
 body=await request.json();text='\n'.join(m.get('content','')for m in body['messages'])
 if '答案校验'in text or '检查项'in text:content=json.dumps({'passed':True,'score':1,'issues':[]})
 elif '改写'in text and 'queries'in text:content=json.dumps({'queries':['压测事项材料要求']},ensure_ascii=False)
 elif 'needs_cross_dept'in text:content=json.dumps({'type':'regulation_consult','depts':['dept_load_fixture'],'entities':{'matter':'压测事项'},'confidence':.99,'user_role':'student','needs_cross_dept':False})
 else:
  await asyncio.sleep(float(os.environ.get("MOCK_ANSWER_DELAY_SECONDS","3")));content='压测事项需提交1份材料。[来源1]'
 return {'id':'mock-load-only','object':'chat.completion','model':'fixture-delay-3000ms','choices':[{'index':0,'message':{'role':'assistant','content':content},'finish_reason':'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0},'synthetic':True}
if __name__=='__main__':uvicorn.run(app,host='0.0.0.0',port=8000,access_log=False)
