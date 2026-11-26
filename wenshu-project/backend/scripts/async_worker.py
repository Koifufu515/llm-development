"""Redis Stream worker：处理异步文档入库、Loop 唤醒等作业。"""
from __future__ import annotations

import asyncio
from pathlib import Path

from app.config import get_settings
from app.deps import build_container
from app.utils.logging import setup_logging


async def process(container, job):
    payload = job.get("payload") or {}
    if job["type"] == "ingest_document":
        path = Path(payload["path"])
        doc = await container.indexer.ingest(
            path, payload["dept_id"], payload["uploaded_by"], ingestion_key=job["_id"]
        )
        doc.setdefault("source", {})["file_name"] = payload.get("original_name", path.name)
        await container.store.update_document(doc["_id"], {"source": doc["source"]})
        from app.pipeline.glossary import GlossaryExtractor
        await GlossaryExtractor(container.store).extract(doc)
        relations = await container.conflict_detector.run_for_document(doc)
        review = await container.review_engine.create_review_order(doc)
        return {"document_id": doc["_id"], "relations": len(relations), "review_id": (review or {}).get("_id")}
    if job["type"] == "maintenance":
        from app.pipeline.lifecycle import DocumentLifecycle
        return {"memory_retention":await container.memory_retention.prune_expired(),
                "expiry_reminders":len(await DocumentLifecycle(container.store,container.indexer).remind_expiring())}
    if job["type"] in {"feedback_received", "run_loop"}:
        async def progress(stage, detail):
            await container.job_queue.update_progress(job["_id"], {
                "stage": stage, "detail": detail,
            }, lease_token=job.get("lease_token"))

        result = await container.loop_engine.run_cycle(progress_callback=progress)
        result["memory_retention"] = await container.memory_retention.prune_expired()
        return result
    raise ValueError(f"未知作业类型: {job['type']}")


async def main():
    settings = get_settings()
    setup_logging(settings.log_level)
    from app.utils.telemetry import configure
    configure(settings)
    container = build_container(settings)
    if container.mongo is not None:
        await container.mongo.connect()
    if hasattr(container.session_store, "connect"):
        await container.session_store.connect()
    import logging
    from contextlib import suppress
    logger = logging.getLogger(__name__)
    async def heartbeat(job):
        while True:
            await asyncio.sleep(container.job_queue.lease_seconds / 3)
            if not await container.job_queue.heartbeat(job):
                raise RuntimeError("job lease lost")
    from datetime import datetime
    from zoneinfo import ZoneInfo
    last_day = None
    try:
        while True:
            try:
                day = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
                if day != last_day:
                    await container.job_queue.enqueue_idempotent("maintenance", {"scheduled":True}, day)
                    if settings.loop_enabled:
                        await container.job_queue.enqueue_idempotent("run_loop", {"scheduled":True}, day)
                    last_day = day
                jobs = await container.job_queue.next_jobs(count=1)
                for job in jobs:
                    work = asyncio.create_task(process(container, job))
                    beat = asyncio.create_task(heartbeat(job))
                    try:
                        done, _ = await asyncio.wait({work, beat}, return_when=asyncio.FIRST_COMPLETED)
                        if beat in done:
                            await beat
                        result = await work
                        await container.job_queue.finish(job, "completed", result)
                    except Exception as exc:
                        await container.job_queue.fail(job, exc)
                    finally:
                        for task in (work, beat):
                            task.cancel()
                            with suppress(asyncio.CancelledError, Exception):
                                await task
                        stored = await container.store.get("async_jobs", job["_id"])
                        if stored and stored["status"] in {"completed", "failed"} and job["type"] == "ingest_document":
                            path = Path(job["payload"]["path"])
                            path.unlink(missing_ok=True)
                            with suppress(OSError): path.parent.rmdir()
            except Exception as exc:
                logger.warning("Worker暂时失败，将恢复轮询: %s", type(exc).__name__)
                await asyncio.sleep(2)
            await asyncio.sleep(.1)
    finally:
        if hasattr(container.session_store, "close"): await container.session_store.close()
        if container.mongo: await container.mongo.close()
        await container.pi_runtime.close()


if __name__ == "__main__":
    asyncio.run(main())
