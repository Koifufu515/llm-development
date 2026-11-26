"""冲突由检测候选进入双部门协调；模型不得自行覆盖制度。"""
from datetime import datetime,timezone

class ConflictWorkflow:
 def __init__(self,store):self.store=store
 async def open(self,relation):
  if relation.get('relation_type')!='conflict':return
  row={**relation,'status':'discovered','history':[],'confirmations':[],'revision':0}
  await self.store.create_once('conflict_cases',row)
  for dept in {relation.get('from_dept'),relation.get('to_dept')} - {None,''}:
   await self.store.create_once('notifications',{'_id':f"conflict:{relation['_id']}:{dept}",'type':'conflict','dept_id':dept,'case_id':relation['_id'],'status':'unread','created_at':datetime.now(timezone.utc)})
 async def advance(self,id_,target,actor,dept_id,note=''):
  row=await self.store.get('conflict_cases',id_)
  if not row:raise KeyError('冲突工单不存在')
  revision=row.get('revision')
  involved={row.get('from_dept'),row.get('to_dept')} - {None,''}
  if dept_id and dept_id not in involved:raise PermissionError('无权处理其它部门冲突')
  allowed={'discovered':{'reviewing','dismissed'},'reviewing':{'coordinating','dismissed'},'coordinating':{'resolved','dismissed'},'resolved':{'closed'},'closed':set(),'dismissed':set()}
  current=row['status']
  if target not in allowed.get(current,set()):raise ValueError('冲突状态迁移无效')
  if not note.strip():raise ValueError('必须记录审核或协调说明')
  if target=='resolved':
   confirmations=set(row.get('confirmations',[]));confirmations.add(dept_id or 'system_admin');row['confirmations']=sorted(confirmations)
   if dept_id and not involved.issubset(confirmations):
    row['history'].append({'target':'confirmation','actor':actor,'dept_id':dept_id,'note':note,'at':datetime.now(timezone.utc)})
    await self._save(row,revision);return row
  row['status']=target;row['history'].append({'from':current,'to':target,'actor':actor,'dept_id':dept_id,'note':note,'at':datetime.now(timezone.utc)})
  await self._save(row,revision);return row

 async def _save(self,row,revision):
  changes={k:v for k,v in row.items()if k!='_id'};changes['revision']=(revision or 0)+1
  if not await self.store.compare_update('conflict_cases',row['_id'],{'revision':revision},changes):
   raise ValueError('工单已被其他管理员更新，请刷新后重试')
  row['revision']=changes['revision']
