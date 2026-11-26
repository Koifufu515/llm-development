"""打包复现源码、脱敏样例和证据；默认排除本机配置、原始文档和用户数据库。"""
import argparse,hashlib,json,os,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.local','.git','.venv','node_modules','.next','__pycache__','.pytest_cache','.playwright-cli','department_files','交付','output'}
ALLOW={'.py','.md','.txt','.json','.ts','.tsx','.css','.svg','.yml','.yaml','.toml','.lock','.js','.mjs','.cjs','.png','.jpg','.jpeg','.command'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--mapping',default='');a=p.parse_args();mapping=json.loads(Path(a.mapping).read_text())if a.mapping else{}
 out=ROOT/'交付';out.mkdir(exist_ok=True);target=out/'文枢-完整方案复现-20261109.zip';manifest=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as z:
  for f in sorted(ROOT.rglob('*')):
   rel=f.relative_to(ROOT)
   if not f.is_file() or any(part in EXCLUDE for part in rel.parts):continue
   if str(rel)=='reports/package-verification.json':continue
   if f.name.startswith('.env') and f.name!='.env.example':continue
   if f.suffix.lower()not in ALLOW and f.name not in {'Dockerfile','Makefile','.gitignore','.dockerignore','.env.example'}:continue
   raw=f.read_bytes()
   try:
    text=raw.decode('utf-8')
    if f.suffix in {'.py','.ts','.tsx','.js'} and any(source in text for source in mapping):raise ValueError('源码含需脱敏标识，拒绝静默改写程序：'+str(rel))
    for source,replacement in sorted(mapping.items(),key=lambda x:-len(x[0])):text=text.replace(source,replacement)
    raw=text.encode('utf-8')
   except UnicodeDecodeError:pass
   manifest.append({'path':str(rel),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)});z.writestr('wenshu-project/'+str(rel),raw)
  z.writestr('wenshu-project/RELEASE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  assert not any(any(p in EXCLUDE for p in Path(n).parts)for n in z.namelist())
 result={'file':str(target),'files':len(manifest)+1,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'crc':'passed'}
 (out/'release.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
