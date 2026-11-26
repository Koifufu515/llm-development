import asyncio
import hashlib
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid4())

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__='kg_users'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    email: Mapped[str]=mapped_column(String(254),unique=True,index=True)
    username: Mapped[str]=mapped_column(String(50),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(128))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)

class Conversation(Base):
    __tablename__='kg_conversations'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    user_id: Mapped[str]=mapped_column(ForeignKey('kg_users.id'),index=True)
    title: Mapped[str]=mapped_column(String(120),default='新对话')
    status: Mapped[str]=mapped_column(String(20),default='active')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
    deleted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)

class Message(Base):
    __tablename__='kg_messages'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    conversation_id: Mapped[str]=mapped_column(ForeignKey('kg_conversations.id'),index=True)
    role: Mapped[str]=mapped_column(String(20))
    content: Mapped[str]=mapped_column(Text,default='')
    extra: Mapped[dict]=mapped_column(JSONB,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)

class Card(Base):
    __tablename__='kg_cards'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    conversation_id: Mapped[str]=mapped_column(ForeignKey('kg_conversations.id'),index=True)
    skill_name: Mapped[str]=mapped_column(String(50))
    revision: Mapped[int]
    payload: Mapped[dict]=mapped_column(JSONB)
    submitted: Mapped[dict|None]=mapped_column(JSONB,nullable=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)

class Plan(Base):
    __tablename__='kg_plans'
    __table_args__=(UniqueConstraint('conversation_id','revision',name='kg_plans_conversation_revision_uq'),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    conversation_id: Mapped[str]=mapped_column(ForeignKey('kg_conversations.id'),index=True)
    title: Mapped[str]=mapped_column(String(120))
    revision: Mapped[int]
    body: Mapped[dict]=mapped_column(JSONB)
    budget: Mapped[dict]=mapped_column(JSONB)
    map_data: Mapped[dict]=mapped_column(JSONB,default=dict)
    quality: Mapped[dict]=mapped_column(JSONB,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)

class Database:
    def __init__(self,settings):
        self.engine=create_async_engine(settings.database_url.replace('postgresql://','postgresql+asyncpg://',1),
           pool_size=8,max_overflow=4,pool_pre_ping=True,echo=False)
        self._sessions=async_sessionmaker(self.engine,expire_on_commit=False)
    @asynccontextmanager
    async def session(self):
        import anyio
        # 业务数据库块只含短数据库操作；断连不能中断事务回滚/连接归还。
        with anyio.CancelScope(shield=True):
            async with self._sessions() as session:yield session
    async def setup(self):
        async with self.engine.begin() as conn:
            await conn.execute(text('SELECT pg_advisory_xact_lock(6250173301)'))
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text('ALTER TABLE kg_users ADD COLUMN IF NOT EXISTS username VARCHAR(50)'))
            await conn.execute(text("UPDATE kg_users SET username=left(split_part(email,'@',1),30)||'-'||left(replace(id,'-',''),12) WHERE username IS NULL"))
            await conn.execute(text('ALTER TABLE kg_users ALTER COLUMN username SET NOT NULL'))
            await conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_kg_users_username ON kg_users(username)'))
            # 保留现有全部数据；移除曾错误添加的会话级唯一约束，允许历史版本。
            old=(await conn.execute(text("SELECT conname FROM pg_constraint WHERE conrelid='kg_plans'::regclass AND contype='u' AND pg_get_constraintdef(oid)='UNIQUE (conversation_id)'"))).scalars().all()
            for name in old:
                quoted=conn.dialect.identifier_preparer.quote(name)
                await conn.execute(text('ALTER TABLE kg_plans DROP CONSTRAINT '+quoted))
            await conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS kg_plans_conversation_revision_uq ON kg_plans(conversation_id,revision)'))
    async def close(self): await self.engine.dispose()
    @asynccontextmanager
    async def lock(self,key):
        """PG会话锁覆盖多个进程；不同会话独立，退出和取消都释放。"""
        number=int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],signed=True)
        import anyio
        conn=await self.engine.connect();acquired=False
        try:
            for _ in range(600):
                acquired=await conn.scalar(text('SELECT pg_try_advisory_lock(:k)'),{'k':number})
                if acquired:break
                await asyncio.sleep(.1)
            if not acquired:raise TimeoutError('该会话仍在处理上一条请求')
            yield
        finally:
            # StreamingResponse断连会取消整个AnyIO作用域，清理须屏蔽其重复取消。
            with anyio.CancelScope(shield=True):
                try:
                    if acquired:await conn.execute(text('SELECT pg_advisory_unlock(:k)'),{'k':number})
                except BaseException:
                    await conn.invalidate()
                    raise
                finally:await conn.close()

async def owned(db,conversation_id,user_id):
    from fastapi import HTTPException
    row=await db.scalar(select(Conversation).where(Conversation.id==str(conversation_id),Conversation.user_id==user_id,Conversation.deleted_at.is_(None)))
    if row is None: raise HTTPException(404,'会话不存在')
    return row

def public(row):
    return {c.name:getattr(row,c.name) for c in row.__table__.columns if c.name!='password_hash'}
