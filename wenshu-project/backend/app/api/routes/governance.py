"""文档治理：生命周期、提醒、术语和跨部门冲突闭环。"""
from typing import Optional
from fastapi import APIRouter,Depends,HTTPException,Request
from pydantic import BaseModel,Field
from app.api.deps import require_admin,scope_dept
from app.api.schemas import ApiResponse
from app.pipeline.lifecycle import DocumentLifecycle
from app.pipeline.glossary import GlossaryExtractor
from app.pipeline.conflict_workflow import ConflictWorkflow

router=APIRouter(prefix='/governance',tags=['governance'])

def authorize(row,scope):
 if scope and scope not in {row.get('dept_id'),row.get('from_dept'),row.get('to_dept')}:
  raise HTTPException(403,'无权访问其它部门资源')

class Decision(BaseModel):
 approved:bool
class ConflictDecision(BaseModel):
 status:str
 note:str=Field(min_length=1,max_length=2000)
class ExpiryUpdate(BaseModel):
 expiry_date:Optional[str]=None

@router.get('/notifications',response_model=ApiResponse)
async def notifications(request:Request,user:dict=Depends(require_admin)):
 store=request.app.state.container.store;scope=scope_dept(user)
 return ApiResponse(data=await store.find('notifications',{'dept_id':scope} if scope else {}))

@router.post('/expiry/check',response_model=ApiResponse)
async def expiry_check(request:Request,user:dict=Depends(require_admin)):
 c=request.app.state.container
 if scope_dept(user):raise HTTPException(403,'全局扫描仅系统管理员可执行')
 return ApiResponse(data=await DocumentLifecycle(c.store,c.indexer).remind_expiring())

@router.post('/documents/{doc_id}/expiry',response_model=ApiResponse)
async def set_expiry(doc_id:str,body:ExpiryUpdate,request:Request,user:dict=Depends(require_admin)):
 from datetime import datetime
 c=request.app.state.container;doc=await c.store.get_document(doc_id)
 if not doc:raise HTTPException(404,'文档不存在')
 authorize(doc,scope_dept(user))
 if body.expiry_date:
  try:datetime.fromisoformat(body.expiry_date)
  except ValueError:raise HTTPException(422,'日期格式无效')
 await c.store.update_document(doc_id,{'expiry_date':body.expiry_date})
 return ApiResponse(data=await c.store.get_document(doc_id))

@router.get('/documents/{doc_id}/history',response_model=ApiResponse)
async def document_history(doc_id:str,request:Request,user:dict=Depends(require_admin)):
 c=request.app.state.container;doc=await c.store.get_document(doc_id)
 if not doc:raise HTTPException(404,'文档不存在')
 authorize(doc,scope_dept(user))
 return ApiResponse(data=await DocumentLifecycle(c.store,c.indexer).history(doc_id))

@router.get('/terms',response_model=ApiResponse)
async def terms(request:Request,user:dict=Depends(require_admin)):
 scope=scope_dept(user);store=request.app.state.container.store
 return ApiResponse(data=await store.find('glossary_candidates',{'dept_id':scope} if scope else {}))

@router.post('/terms/{id_}/review',response_model=ApiResponse)
async def review_term(id_:str,body:Decision,request:Request,user:dict=Depends(require_admin)):
 store=request.app.state.container.store;item=await store.get('glossary_candidates',id_)
 if not item:raise HTTPException(404,'术语不存在')
 authorize(item,scope_dept(user))
 try:return ApiResponse(data=await GlossaryExtractor(store).review(id_,user['id'],body.approved))
 except ValueError as exc:raise HTTPException(409,str(exc))

@router.get('/conflicts',response_model=ApiResponse)
async def conflicts(request:Request,user:dict=Depends(require_admin)):
 rows=await request.app.state.container.store.find('conflict_cases');scope=scope_dept(user)
 return ApiResponse(data=[r for r in rows if not scope or scope in {r.get('from_dept'),r.get('to_dept')}])

@router.post('/conflicts/{id_}/transition',response_model=ApiResponse)
async def conflict_transition(id_:str,body:ConflictDecision,request:Request,user:dict=Depends(require_admin)):
 try:return ApiResponse(data=await ConflictWorkflow(request.app.state.container.store).advance(id_,body.status,user['id'],scope_dept(user),body.note))
 except KeyError:raise HTTPException(404,'冲突不存在')
 except PermissionError as exc:raise HTTPException(403,str(exc))
 except ValueError as exc:raise HTTPException(409,str(exc))


class GapResolution(BaseModel):
 doc_ids:list[str]=Field(min_length=1,max_length=20)
 note:str=Field(min_length=1,max_length=2000)

@router.get('/knowledge-workorders',response_model=ApiResponse)
async def knowledge_workorders(request:Request,user:dict=Depends(require_admin)):
 scope=scope_dept(user);store=request.app.state.container.store
 return ApiResponse(data=await store.find('knowledge_workorders',{'dept_id':scope}if scope else{}))

@router.post('/knowledge-workorders/{id_}/resolve',response_model=ApiResponse)
async def resolve_gap(id_:str,body:GapResolution,request:Request,user:dict=Depends(require_admin)):
 from app.loop.knowledge_gaps import KnowledgeGapManager
 try:return ApiResponse(data=await KnowledgeGapManager(request.app.state.container.store).resolve(id_,user['id'],scope_dept(user),body.doc_ids,body.note))
 except KeyError:raise HTTPException(404,'工单不存在')
 except PermissionError as exc:raise HTTPException(403,str(exc))
 except ValueError as exc:raise HTTPException(409,str(exc))
