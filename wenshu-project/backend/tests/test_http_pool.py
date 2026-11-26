import pytest,httpx
from app.llm.client import LLMClient

@pytest.mark.asyncio
async def test_completion_and_stream_share_client_and_close_cleanly():
 calls=[]
 async def handle(request):
  import json
  body=json.loads(request.content);calls.append(body)
  if body.get('stream'):
   return httpx.Response(200,headers={'content-type':'text/event-stream'},text='data: {"choices":[{"delta":{"content":"流式"}}]}\n\ndata: [DONE]\n\n')
  return httpx.Response(200,json={'choices':[{'message':{'content':'回答'}}],'usage':{'prompt_tokens':1,'completion_tokens':1}})
 class Fixture(LLMClient):
  def name(self):return 'fixture'
 client=Fixture('http://fixture.invalid','not-a-real-key','fixture')
 pooled=httpx.AsyncClient(transport=httpx.MockTransport(handle));client._client=pooled
 assert await client.complete([{'role':'user','content':'问题'}])=='回答'
 assert ''.join([s async for s in client.stream([{'role':'user','content':'问题'}])])=='流式'
 assert client._http()is pooled and len(calls)==2
 await client.close();assert pooled.is_closed and client._client is None
