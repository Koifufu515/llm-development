"""健康检查 / 就绪探针。"""
from __future__ import annotations

from fastapi import APIRouter, Request
import asyncio
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(request: Request):
    container = request.app.state.container
    issues = []
    if container.settings.storage_mode == "mongo":
        try:
            if container.mongo is None or container.mongo.db is None:
                raise RuntimeError("not connected")
            await asyncio.wait_for(container.mongo.db.command("ping"),2)
        except Exception:
            issues.append("mongodb")
    if hasattr(container.session_store,"_redis"):
        try:
            if container.session_store._redis is None:raise RuntimeError("not connected")
            await asyncio.wait_for(container.session_store.redis.ping(),2)
        except Exception:
            issues.append("redis")
    if container.settings.vector_backend == "milvus":
        try:
            await asyncio.wait_for(container.vector_store._ready(),3)
        except Exception:
            issues.append("milvus")
    if issues:
        return JSONResponse(status_code=503, content={"status": "not_ready", "issues": issues})
    return {"status": "ready"}
