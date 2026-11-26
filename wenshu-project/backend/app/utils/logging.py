"""统一日志配置。"""
from __future__ import annotations

import logging
import sys
import json

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def format(self,record):
        from app.utils.telemetry import current_trace_id
        row={"timestamp":self.formatTime(record),"level":record.levelname,"logger":record.name,"message":record.getMessage(),"trace_id":current_trace_id()}
        if record.exc_info:row["exception"]=self.formatException(record.exc_info)
        return json.dumps(row,ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter()
    )
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers = [handler]
    # 降低第三方库噪音
    for noisy in ("uvicorn.access", "httpx", "httpcore", "chromadb", "numexpr"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
