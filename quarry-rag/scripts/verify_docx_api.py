"""真实Word上传→共享卷→worker→向量化→检索→段落引用，验后清理本实验文档。"""
import asyncio,io,json,re,sys,subprocess
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from docx import Document
import httpx
from quarry.infra.db import init_pool,close_pool,acquire
async def main():
 name='word-acceptance-'+uuid4().hex+'.docx';did=None;key=re.search(r'qr_[\w-]+',Path('private/ingest-key.txt').read_text()).group();auth={'Authorization':f'Bearer {key}'}
 d=Document();d.add_heading('Word验收差旅限额',1);d.add_paragraph('成都住宿报销上限为480元。');t=d.add_table(rows=2,cols=2);t.cell(0,0).text='城市';t.cell(0,1).text='住宿限额';t.cell(1,0).text='成都';t.cell(1,1).text='480元';b=io.BytesIO();d.save(b)
 await init_pool()
 try:
  async with httpx.AsyncClient(base_url='http://127.0.0.1:8113',headers=auth,timeout=20)as c:
   r=await c.post('/v1/documents',params={'collection_slug':'corp-policy'},files={'file':(name,b.getvalue())});assert r.status_code==200;did=r.json()['document_id']
   for _ in range(30):
    state=(await c.get('/v1/documents/'+did)).json()
    if state.get('status')in['ready','failed']:break
    await asyncio.sleep(.4)
   assert state.get('status')=='ready',state
   r=await c.post('/v1/search',json={'collection':'corp-policy','query':'Word验收成都住宿报销上限是多少','top_k':5});assert r.status_code==200
   es=[e for e in r.json()['evidences']if e['citation']['source_uri'].endswith(name)];assert es and all(e['citation']['locator_kind']=='paragraph'for e in es)
   assert any('480元'in e['context']and '|'in e['context']for e in es)
  result={'upload_ready':True,'real_evidence_count':len(es),'table_value_preserved':True,'locator_kind':'paragraph'};Path('reports/docx-api.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result)
 finally:
  if did:
   from uuid import UUID
   async with acquire()as c:await c.execute('DELETE FROM documents WHERE id=$1',UUID(did))
  await close_pool()
  code='from pathlib import Path;import sys; (Path("/app/corpus/corp-policy")/sys.argv[1]).unlink(missing_ok=True)'
  p=subprocess.run(['docker','--context','colima-knowgo','compose','-p','quarry-rag','exec','-T','worker','python','-c',code,name],capture_output=True,text=True);assert p.returncode==0
if __name__=='__main__':asyncio.run(main())
