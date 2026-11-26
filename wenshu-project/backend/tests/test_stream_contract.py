import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.harness.agents.answer_agent import AnswerAgent
from app.harness.agents.verifier_agent import VerifierAgent
from app.harness.base import Answer,VerificationResult

@pytest.mark.asyncio
async def test_python_deltas_emitted_before_generation_finishes():
 class LLM:
  async def stream(self,*a,**kw):
   yield '第一段'
   assert collected==['第一段']
   yield '第二段'
 collected=[]
 async def on_delta(delta):collected.append(delta)
 answer=await AnswerAgent(LLM(),None).generate('问题',[{'doc_id':'d','content':'制度原文'}],on_delta=on_delta)
 assert collected==['第一段','第二段'] and answer.content=='第一段第二段'

@pytest.mark.asyncio
async def test_verifier_sees_identical_complete_numbered_evidence():
 content='甲'*600+'截止第八周'
 class LLM:
  async def complete_json(self,messages,**kw):
   assert '[来源1] '+content in messages[1]['content']
   return {'passed':True,'score':.95,'issues':[]}
 assert (await VerifierAgent(LLM()).verify('何时',Answer(content='第八周'),[{'content':content}])).passed

@pytest.mark.parametrize('invalid',[{},None,{'passed':'false','score':1},{'passed':True,'score':2}])
def test_verification_invalid_output_never_passes(invalid):
 assert not VerificationResult.from_dict(invalid).passed

def test_stream_frames_keep_dept_and_server_identity(monkeypatch):
 with TestClient(app) as client:
  token=client.post('/api/v1/auth/login',json={'username':'student','password':'student123'}).json()['data']['token']
  async def answer(query,**kwargs):
   assert kwargs['dept_ids']==['dept_jwc'] and kwargs['user_role']=='student'
   await kwargs['event_callback']('stage',{'stage':'retrieval'})
   await kwargs['event_callback']('draft_delta',{'delta':'未校验','verified':False})
   return {'session_id':kwargs['session_id'],'answer':'正式答案','citations':[]}
  monkeypatch.setattr(app.state.container.orchestrator,'answer',answer)
  r=client.post('/api/v1/chat/stream',headers={'Authorization':'Bearer '+token},json={'query':'问','dept_ids':['dept_jwc']})
  assert r.status_code==200
  assert r.text.index('event: stage')<r.text.index('event: draft_delta')<r.text.index('event: result')
  assert 'data: [DONE]'in r.text
