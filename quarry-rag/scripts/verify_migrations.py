"""仅创建并删除本脚本命名的空临时数据库，验证每一步升降；不接触业务数据。"""
import asyncio,os,json,sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import asyncpg
from quarry.infra.settings import get_settings
async def main():
 s=get_settings();db='quarry_migration_'+uuid4().hex[:10];out=[]
 args=dict(host=s.postgres_host,port=s.postgres_port,user=s.postgres_user,password=s.postgres_password.get_secret_value())
 c=await asyncpg.connect(database=s.postgres_db,**args)
 await c.execute(f'CREATE DATABASE {db}')
 try:
  d=await asyncpg.connect(database=db,**args);await d.execute('CREATE EXTENSION vector');await d.close()
  env=os.environ.copy();env['POSTGRES_DB']=db
  for direction,target in [('upgrade',f'{n:04d}')for n in range(1,9)]+[('downgrade',f'{n:04d}'if n else 'base')for n in range(7,-1,-1)]+[('upgrade','head')]:
   proc=await asyncio.create_subprocess_exec(sys.executable,'-m','alembic',direction,target,env=env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT);b,_=await proc.communicate();text=b.decode();text=text.replace(s.postgres_password.get_secret_value(),'<REDACTED>');out.append(dict(direction=direction,target=target,exitcode=proc.returncode,output=text));assert proc.returncode==0,(direction,target,text)
 finally:
  await c.execute(f'DROP DATABASE {db}');await c.close();Path('reports/migrations-roundtrip.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print('8次逐步升级、8次逐步回退、1次空库全量升级通过')
if __name__=='__main__':asyncio.run(main())
