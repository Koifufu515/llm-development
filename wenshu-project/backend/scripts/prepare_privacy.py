"""本机生成样例名册的出站替换映射，不上传，不打印姓名/学号。"""
import json,re,os,sys
from pathlib import Path
from docx import Document

def prepare(root:Path):
 source=root/'department_files';names=set();identifiers=set()
 for p in source.rglob('*.docx'):
  if '分组安排'not in p.name:continue
  doc=Document(p)
  for table in doc.tables:
   for row in table.rows:
    cells=[c.text.strip()for c in row.cells]
    if len(cells)>=6 and re.fullmatch(r'\d+',cells[0]):
     identifiers.add(cells[1]);names.update([cells[2],cells[5]])
  for p in doc.paragraphs:
   for name,id_ in re.findall(r'([\u4e00-\u9fff]{2,5})\s*[(（]([A-Za-z0-9]+)[)）]',p.text):names.add(name);identifiers.add(id_)
 names.discard('');identifiers.discard('')
 mapping={name:f'【姓名{i:03}】'for i,name in enumerate(sorted(names),1)}
 mapping.update({id_:f'【编号{i:03}】'for i,id_ in enumerate(sorted(identifiers),1)})
 target=root/'.local/private/privacy-map.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(mapping,ensure_ascii=False,indent=2));target.chmod(0o600)
 return target,mapping

if __name__=='__main__':
 root=Path(__file__).resolve().parents[2];path,m=prepare(root);print(json.dumps({'mapping_file':str(path),'replacement_count':len(m),'local_only':True},ensure_ascii=False))
