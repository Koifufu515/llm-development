import pytest
from langchain_core.messages import AIMessageChunk
from app.full.events import EventStream,EmitSink,make_event
from app.full.streaming import _stream_agent,_scrub_leak_text

class ScriptedAgent:
    def __init__(self,rounds):self.rounds=rounds
    async def astream_events(self,*args,**kwargs):
        for chunks in self.rounds:
            for chunk in chunks:yield {'event':'on_chat_model_stream','data':{'chunk':chunk}}
            yield {'event':'on_chat_model_end','data':{}}

def chunk(text='',tool=False):
    return AIMessageChunk(content=text,tool_call_chunks=[{'name':'lookup','args':'{}','id':'x','index':0}] if tool else [])
async def run(rounds,**kwargs):
    events=[]
    async def emit(role,content):events.append({'role':role,'content':content})
    text=await _stream_agent(ScriptedAgent(rounds),{}, {},EmitSink(emit),**kwargs)
    return text,events

@pytest.mark.asyncio
async def test_tool_first_round_keeps_all_later_body_and_budget():
    text,events=await run([[chunk(tool=True)],[chunk('逐日正文。')],[chunk('预算表。')]])
    assert text=='逐日正文。预算表。'
    assert ''.join(e['content'] or '' for e in events if e['role']=='assistant')==text
    assert not any(e['role']=='assistant_reset' for e in events)

@pytest.mark.asyncio
async def test_first_body_is_restored_when_it_was_buffered():
    text,events=await run([[chunk('正文开头。')],[chunk('接下来的预算。')]])
    assert text=='正文开头。接下来的预算。'
    assert events[-2]['role']=='assistant_reset' and events[-1]['content']==text

@pytest.mark.asyncio
async def test_leak_is_reset_and_never_remains_in_final_text():
    text,events=await run([[chunk(tool=True)],[chunk('正常的旅游建议。'),chunk('请确保调用的工具名称和参数正确。')]])
    assert text=='正常的旅游建议。'
    assert events[-2]['role']=='assistant_reset' and events[-1]['content']==text

@pytest.mark.asyncio
async def test_buffered_code_owned_output_does_not_emit_model_draft():
    text,events=await run([[chunk('模型候选草稿。')]],buffer_all=True,defer_push=True)
    assert text=='模型候选草稿。' and not events

@pytest.mark.asyncio
async def test_producer_failure_always_closes_event_consumer():
    stream=EventStream()
    try:
        stream.push(make_event('assistant','部分输出'))
        raise RuntimeError('故障注入')
    except RuntimeError:stream.push(make_event('error','失败'))
    finally:stream.push(make_event('done','finish',500));stream.close()
    assert [e['role'] async for e in stream]==['assistant','error','done']

def test_scrub_keeps_normal_lists_and_removes_protocol_blocks():
    value='正常正文。\n我将使用以下参数调用 record_tool：\n- city: 苏州\n\n旅行建议正文。'
    clean=_scrub_leak_text(value)
    assert 'record_tool' not in clean and 'city:' not in clean and '旅行建议正文' in clean


@pytest.mark.asyncio
async def test_rendered_plan_longer_than_one_chunk_finishes_without_loss():
    from app.full.streaming import _push_rendered
    from app.full.events import EventStream
    stream=EventStream();text='真实长正文与预算均需完整推送。'*9
    await _push_rendered(stream,text);stream.close()
    events=[e async for e in stream]
    assert len(events)>1 and ''.join(e['content'] for e in events)==text
    assert all(e['role']=='assistant' for e in events)
