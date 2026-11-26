"""本机交互创建独立管理员；不打印密码。"""
import asyncio,getpass
from app.config import Settings
from app.deps import build_container
from app.auth import AuthService
async def main():
 c=build_container(Settings());await c.mongo.connect()
 try:
  username=input('管理员账号：').strip();password=getpass.getpass('密码（至少12字符）：')
  if not username or len(password)<12:raise ValueError('账号不能为空，密码至少12字符')
  if await c.store.get('users',username):raise ValueError('账号已存在，未覆盖')
  await c.store.upsert('users',AuthService._to_user({'username':username,'password':password,'name':username,'role':'admin','dept_id':''}));print('管理员已创建')
 finally:await c.mongo.close()
if __name__=='__main__':asyncio.run(main())
