"""把知识缺口反馈聚类为部门补充资料工单；不自动生成或修改制度事实。"""
import hashlib
from datetime import datetime,timezone
from app.loop.skill_miner import SkillMiner

class KnowledgeGapManager:
 def __init__(self,store,embeddings=None):self.store=store;self.embeddings=embeddings
 async def collect(self,cases,reflection):
  explicit=reflection.get('knowledge_gaps')or[]
  missing={g.get('query') for g in explicit if isinstance(g,dict)}
  selected=[c for c in cases if c.get('query')in missing or (c.get('detail')or{}).get('root_cause')=='knowledge_gap']
  groups={}
  for case in selected:
   department=(case.get('detail')or{}).get('dept_id')or 'unassigned'
   groups.setdefault(department,[]).append(case)
  created=[]
  for dept,rows in groups.items():
   queries=[r.get('query','')for r in rows];clusters=[]
   if self.embeddings and len(rows)>1:
    try:
     vectors=await self.embeddings.embed(queries)
     clusters=SkillMiner(self.store).cluster(queries,vectors)
    except Exception:clusters=[]
   covered={i for cluster in clusters for i in cluster}
   clusters.extend([[i]for i in range(len(rows))if i not in covered])
   for cluster in clusters:
    examples=sorted(set(queries[i]for i in cluster))
    key=hashlib.sha256((dept+':'+':'.join(examples)).encode()).hexdigest()
    item={'_id':'gap_'+key,'dept_id':dept,'status':'pending','examples':examples,'source_feedback_ids':[rows[i].get('_id')for i in cluster],'kind':'knowledge_gap','note':'待部门核实并补充官方资料，不得由模型补写事实','created_at':datetime.now(timezone.utc)}
    saved=await self.store.create_once('knowledge_workorders',item);created.append(saved['_id'])
  return created
 async def resolve(self,id_,actor,dept,doc_ids,note):
  row=await self.store.get('knowledge_workorders',id_)
  if not row:raise KeyError('知识工单不存在')
  if dept and row['dept_id']!=dept:raise PermissionError('无权处理其它部门工单')
  if not doc_ids or not note.strip():raise ValueError('须绑定补充的官方文档并填写说明')
  for id_ in doc_ids:
   doc=await self.store.get_document(id_)
   if not doc or doc.get('status')!='active' or (row['dept_id']!='unassigned' and doc.get('dept_id')!=row['dept_id']):raise ValueError('补充资料不存在、未生效或不属于工单部门')
  row.update(status='resolved',source_doc_ids=doc_ids,resolution=note,reviewed_by=actor,resolved_at=datetime.now(timezone.utc))
  await self.store.upsert('knowledge_workorders',row);return row
