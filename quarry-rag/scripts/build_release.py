"""构建不含本机密钥/数据库/虚拟环境的交付包，并逐值扫描已配置凭证。"""
from pathlib import Path
import hashlib,json,re,zipfile
from dotenv import dotenv_values
root=Path(__file__).resolve().parents[1]
secrets=[]
for k,v in dotenv_values(root/'.env').items():
 if v and len(v)>=10 and any(t in k for t in ['KEY','PASSWORD','SECRET']):secrets.append(v.encode())
for p in (root/'private').glob('*.txt'):
 secrets += [m.encode()for m in re.findall(r'qr_[A-Za-z0-9_-]{20,}',p.read_text())]
roots=['quarry','sdk','tests','scripts','.github','docs','corpus','official','eval','reports','snapshots','migrations','docker']
files=[]
for name in roots:
 for p in (root/name).rglob('*'):
  if not p.is_file():continue
  parts=p.relative_to(root).parts
  if any(x in ['__pycache__','.pytest_cache','.ruff_cache','.venv','private']or x.startswith('._')for x in parts):continue
  if p.suffix in ['.pyc','.log']or p.name=='.DS_Store':continue
  if name=='reports' and p.name in ['package-audit.json','unpack-final-tests.txt']:continue
  files.append(p)
for name in ['README.md','pyproject.toml','uv.lock','Dockerfile','docker-compose.yml','alembic.ini','verify_env.py','.gitignore','.dockerignore','.env.example']:
 files.append(root/name)
files=sorted(set(files));bad=[]
for p in files:
 data=p.read_bytes()
 if p.suffix=='.gz':
  import gzip
  data+=gzip.decompress(data)
 if any(secret in data for secret in secrets):bad.append(str(p.relative_to(root)))
assert not bad,'凭证扫描命中文件：'+str(bad)
out=root/'交付';out.mkdir(exist_ok=True);dest=out/'Quarry-RAG-完整复现-20261109.zip'
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:
  info=zipfile.ZipInfo('quarry-rag/'+p.relative_to(root).as_posix(),date_time=(2026,11,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
with zipfile.ZipFile(dest)as z:
 assert z.testzip()is None
 required=['docker/init-db.sql','scripts/bootstrap.sh','alembic.ini','uv.lock','docker-compose.yml']
 assert all('quarry-rag/'+name in z.namelist()for name in required),'缺失部署必需文件'
 assert not any('/private/'in name or name.endswith('/.env')or name.endswith('/.env.docker')for name in z.namelist()),'包含本机配置'
code_files=[p for p in files if (p.suffix in ['.py','.sql']and p.relative_to(root).parts[0]in ['quarry','sdk','migrations','scripts','tests','docker'])or p.name in ['Dockerfile','docker-compose.yml','pyproject.toml','uv.lock']]
# 代码摘要用于核对独立解包与本机冻结版本。
code_sha=hashlib.sha256(''.join(p.relative_to(root).as_posix()+':'+hashlib.sha256(p.read_bytes()).hexdigest()+'\n'for p in code_files).encode()).hexdigest()
result={'file':str(dest),'files':len(files),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'crc_ok':True,'configured_secret_matches':0,'code_sha256':code_sha}
(root/'reports/package-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
