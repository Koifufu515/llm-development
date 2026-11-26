import asyncio
import hashlib
import os
import secrets
from datetime import datetime,timedelta,timezone
from uuid import UUID

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.config import PROJECT_ROOT
from app.full.database import User

bearer=HTTPBearer(auto_error=False)

def signing_key():
    configured=os.getenv('JWT_SECRET','')
    if configured: return configured
    path=PROJECT_ROOT/'data'/'.jwt_secret'
    path.parent.mkdir(exist_ok=True)
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f: f.write(secrets.token_hex(48))
    except FileExistsError: pass
    return path.read_text().strip()

def password_bytes(value):
    # bcrypt 72字节上限；先SHA256定长，版本前缀明确，支持中文长口令。
    return hashlib.sha256(value.encode()).hexdigest().encode()

async def password_hash(value):
    hashed=await asyncio.to_thread(bcrypt.hashpw,password_bytes(value),bcrypt.gensalt(rounds=12))
    return 'sha256:'+hashed.decode()

async def verify_password(value,hashed):
    try: return await asyncio.to_thread(bcrypt.checkpw,password_bytes(value),hashed.removeprefix('sha256:').encode())
    except ValueError: return False

def token_for(user_id):
    now=datetime.now(timezone.utc)
    return jwt.encode({'sub':user_id,'iat':now,'exp':now+timedelta(hours=24),'iss':'knowgo','aud':'knowgo-web'},signing_key(),algorithm='HS256')

async def current_user(request:Request,credentials:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if credentials is None: raise HTTPException(401,'请先登录',headers={'WWW-Authenticate':'Bearer'})
    try:
        claims=jwt.decode(credentials.credentials,signing_key(),algorithms=['HS256'],issuer='knowgo',audience='knowgo-web',options={'require':['exp','sub','iat']})
        user_id=str(UUID(claims['sub']))
    except (jwt.PyJWTError,ValueError,TypeError,KeyError): raise HTTPException(401,'登录已过期或无效') from None
    async with request.app.state.full_db.session() as db:
        user=await db.get(User,user_id)
        if user is None: raise HTTPException(401,'用户不存在')
        return user
