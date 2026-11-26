"""创建脱敏本地复现包；不携带PG用户数据、JWT签名材料、真实env或依赖缓存。"""
from pathlib import Path
import hashlib,json,re,zipfile,os
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'知行旅行助手_原方案复现_2026-10-31.zip'
blocked={'.git','.venv','.tools','node_modules','__pycache__','.pytest_cache','.playwright-cli','.ruff_cache','logs'}
prefixes=('app/','scripts/','tests/','evaluation/','infra/rail-mcp/','docs/','data/full_guides/','data/full_rag/','data/guides/','reports/','output/playwright/')
root_names={'README.md','pyproject.toml','uv.lock','.python-version','.env.example','.gitignore','compose.yaml','compose.redis.yaml','启动后端.command','环境验证.json'}
files=[]
for parent,dirs,names in os.walk(ROOT):
 dirs[:]=[d for d in dirs if d not in blocked]
 for name in names:
  p=Path(parent)/name;rel=p.relative_to(ROOT).as_posix()
  if p.is_symlink()or name=='.DS_Store' or name.endswith(('.zip','.pyc','.env')) or '.jwt_secret'in name:continue
  if rel not in root_names and not rel.startswith(prefixes):continue
  if rel.startswith('reports/')and not(name.startswith('reference-')or name in {'指标实测报告.md','简历项目描述.md','原方案复现对照.md','面经填空实测对照.md','full_rag_validation_set.json'}or rel.startswith('reports/验证日志/')):continue
  if rel.startswith('output/')and not name.startswith('reference-'):continue
  if name in {'代码与数据文件清单.json','本轮交付清单.json'}:continue
  files.append(p)
secret_values=[]
for name in ('.env','外部服务配置.env'):
 for key,value in dotenv_values(ROOT/name).items():
  if value and len(value)>=12 and any(marker in key.upper()for marker in ('KEY','SECRET','PASSWORD','MCP_API')):secret_values.append((key,value.encode()))
jwt=ROOT/'data/.jwt_secret'
if jwt.exists():secret_values.append(('JWT_SIGNING_SECRET',jwt.read_bytes().strip()))
manifest={}
for p in files:
 raw=p.read_bytes();rel=p.relative_to(ROOT).as_posix()
 for key,value in secret_values:
  if value and value in raw:raise SystemExit('拒绝打包：发现本机凭证，文件='+rel+'，字段='+key)
 if p.suffix in {'.json','.md','.txt','.html','.py','.sh','.yaml','.toml'} and re.search(rb'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',raw):raise SystemExit('拒绝打包：发现JWT格式文本，文件='+rel)
 manifest[rel]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
manifest_path=ROOT/'docs/代码与数据文件清单.json';manifest_path.write_text(json.dumps({'scope':'不包含本清单自身及压缩包自身；本地原始凭证扫描通过。','files':manifest},ensure_ascii=False,indent=2));files.append(manifest_path)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as archive:
 for p in sorted(files):archive.write(p,'knowgo-travel/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(DEST)as archive:
 assert archive.testzip()is None
 for rel,expected in manifest.items():assert hashlib.sha256(archive.read('knowgo-travel/'+rel)).hexdigest()==expected['sha256']
 assert not any(n.endswith('/.env')or n.endswith('/外部服务配置.env')or'.jwt_secret'in n for n in archive.namelist())
report={'archive':DEST.name,'bytes':DEST.stat().st_size,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'files':len(files),'crc_and_file_hash_verified':True,'credential_scan_passed':True,'actual_credentials_embedded':False,'scope':'包包含代码/冻结依赖/攻略/Chroma/报告；不携带现有PG用户数据和真实env。需按README配置本机环境，不冒称已在另一台机器部署。'}
(ROOT/'reports/本轮交付清单.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
