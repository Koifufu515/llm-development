"""真实Qwen两轮Loop证据；所有反馈均为明确标记的脚本验收，非线上用户指标。"""
import asyncio,json,copy,uuid
from pathlib import Path
from datetime import datetime,timezone
from dotenv import load_dotenv
from app.config import Settings
from app.deps import build_container
from app.loop.governance import validate_artifact

async def main():
 root=Path(__file__).resolve().parents[2];load_dotenv(root/'.env',override=False)
 source=build_container(Settings());await source.mongo.connect()
 c=build_container(Settings(storage_mode='memory',vector_backend='memory',dept_agents_enabled=False,loop_phase='human_in_loop'))
 report={'scope':'独立内存事实/策略平面，真实Qwen与Embedding/重排；脚本反馈/回放样例，不是线上采纳率或真实用户规模','cycles':[]}
 out=root/'reports/loop-live-proof.json'
 def save():out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str))
 try:
  docs=[d for d in await source.store.list_documents(status='active')if 'student'in d.get('access_roles',['student'])]
  rows=[]
  for doc in docs:
   await c.store.insert_document(doc)
   rows.extend(await source.store.list_chunks_by_doc(doc['_id']))
  await c.store.insert_chunks(rows);c.bm25.index(rows)
  vectors=await c.embeddings.embed([r['content']for r in rows])
  for row,vec in zip(rows,vectors):await c.vector_store.add(row['_id'],vec,{'doc_id':row['doc_id'],'dept_id':row['dept_id'],'chunk_index':row['chunk_index']})
  for dept in await source.store.list_departments():await c.store.upsert_department(dept)
  await c.rule_engine.seed_defaults();await c.hook_engine.seed_defaults()
  query='强降雨天气可以在校园骑行吗？'
  before=await c.orchestrator.answer(query,user_id='scripted-proof',dept_ids=['dept_hqaq']);report['before']=before;save()
  rubric='回答必须使用【结论】【制度依据】【注意事项】三个标题；只回答原文支持的内容，引用外层来源编号，不能用表格序号作为引用。'
  await c.feedback_collector.collect_explicit(before['session_id'],'scripted-proof',query,before['answer'],'correction',{'rule':rubric,'dept_id':'dept_hqaq','origin':'scripted-format-feedback'})
  cycle1=await c.loop_engine.run_cycle();report['cycles'].append(cycle1)
  pending=await c.store.list_rules(status='pending');target=next(r for r in pending if r.get('content')==rubric)
  assert not any(r.get('content')==rubric for r in await c.rule_engine.active_rules(['dept_hqaq']))
  validate_artifact('rule',target);target.update(status='active',reviewed_by='scripted-human-review-simulation',reviewed_at=datetime.now(timezone.utc).isoformat());await c.store.upsert_rule(target)
  after=await c.orchestrator.answer(query,user_id='scripted-proof-after',dept_ids=['dept_hqaq']);report['after_review']=after;report['format_rule_changed_answer']=all(t in after['answer']for t in ['【结论】','【制度依据】','【注意事项】']);save()
  # 20条显式脚本回放，用于验证原方案7天/20次阈值及真实Embedding聚类。
  for i in range(20):
   q='电子信息和机械开题分别要带几份纸质报告？'
   await c.store.insert_trace({'_id':'scripted_trace_'+str(i),'query':q,'answer':'脚本注入的错误来源编号示例[来源99]','success':False,'verification':{'passed':False},'intent':{'type':'regulation_consult','depts':['dept_zfxy']},'user_id':'scripted_replay_'+str(i),'session_id':'scripted_replay_'+str(i),'created_at':datetime.now(timezone.utc).isoformat(),'origin':'scripted-replay-not-live-user'})
   await c.feedback_collector.collect_explicit('scripted_replay_'+str(i),'scripted_replay_'+str(i),q,'脚本注入的错误来源编号示例[来源99]','correction',{'rule':'引用必须对应检索证据的外层来源编号，不能使用表格行序号。','dept_id':'dept_zfxy','origin':'scripted-replay-not-live-user'})
  cycle2=await c.loop_engine.run_cycle();report['cycles'].append(cycle2)
  report['skills']=await c.store.list_skills();report['rules']=await c.store.list_rules();report['knowledge_workorders']=await c.store.find('knowledge_workorders');report['pending_feedback_after']=len(await c.feedback_collector.pending());report['source_database_modified']=False;report['scripted_replay_count']=20;save()
  print(json.dumps({'cycles':len(report['cycles']),'format_changed':report['format_rule_changed_answer'],'skills':len(report['skills']),'pending_feedback_after':report['pending_feedback_after'],'scripted_replays':20},ensure_ascii=False))
 finally:
  await source.mongo.close();await c.pi_runtime.close();await c.llm.close();await c.relay.close()

if __name__=='__main__':asyncio.run(main())
