import asyncio
import logging
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from pydantic import BaseModel, Field

from app.agents.travel_agent import create_travel_agent
from app.config import Settings, PROJECT_ROOT
from app.core.checkpointer import open_checkpointer
from app.core.state import TravelState, missing_fields
from app.core.transitions import confirmation_context
from app.utils.llm_factory import get_deepseek_llm
from app.mcp_core.client import ProjectMCPManager
from app.tools.rail_tools import make_rail_tool
from app.core.rail import render_ticket_table
from app.core.telemetry import RequestMetrics
from app.core.store import open_store
from app.services.knowledge import KnowledgeBase
from app.services.remote import RemoteProviders
from app.api.delivery import router as delivery_router
from app.tools.completion_tools import make_completion_tools

from app.full.api import router as full_router
from app.full.database import Database
from app.full.workflow import Services

logger = logging.getLogger("knowgo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with open_checkpointer(Settings()) as saver, open_store(Settings()) as store:
        app.state.store = store
        app.state.remote = RemoteProviders()
        app.state.knowledge = KnowledgeBase()
        await asyncio.to_thread(app.state.knowledge.load)
        app.state.checkpointer = saver
        app.state.mcp_manager = ProjectMCPManager()
        await app.state.mcp_manager.initialize()
        app.state.weather_tools = [*app.state.mcp_manager.tools.get('weather', []), make_rail_tool(app.state.mcp_manager)]
        # 首阶段串行处理写请求，避免同一 thread_id 的并行更新覆盖。
        app.state.write_lock = asyncio.Lock()
        builder = StateGraph(TravelState)
        builder.add_node("read_only", lambda state: {})
        builder.add_edge(START, "read_only")
        builder.add_edge("read_only", END)
        app.state.state_reader = builder.compile(checkpointer=saver)
        app.state.full_db = Database(Settings())
        await app.state.full_db.setup()
        app.state.full = Services(app)
        await app.state.full.knowledge.load()
        try:
            yield
        finally:
            await app.state.full.close()
            await app.state.full_db.close()


app = FastAPI(title="知行旅行助手", version="0.5.0", lifespan=lifespan)


app.include_router(delivery_router)
app.include_router(full_router)
app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "app/static"), name="assets")

class SessionOptions(BaseModel):
    user_id: UUID | None = None

class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(min_length=1, max_length=4000, pattern=r"\S")


def state_view(state: dict) -> dict:
    requirement = state.get("user_requirement", {})
    return {
        "current_step": state.get("current_step", "requirement_collection"),
        "user_requirement": requirement,
        "missing_fields": missing_fields(requirement),
        "requirement_ready": bool(requirement) and not missing_fields(requirement),
        "requirement_revision": state.get("requirement_revision", 0),
        "requirement_confirmed": state.get("requirement_confirmed", False),
        "confirmed_revision": state.get("confirmed_revision"),
        "selected_destination": state.get("selected_destination"),
        "downstream": {key: state.get(key) for key in ("transport_options", "selected_transport", "accommodation_options", "itinerary", "budget")},
        "message_count": len(state.get("messages", [])),
        "planning_result": state.get("planning_result"),
    }


@app.get("/")
async def root():
    return {"status": "ok", "message": "知行旅行助手后端已启动", "stage": "需求收集"}


@app.get("/health/config")
async def check_config():
    settings = Settings()
    return {
        "provider": settings.model_provider, "model": settings.qwen_model if settings.model_provider == "qwen" else settings.deepseek_model,
        "model_configured": settings.model_configured,
        "database": "postgresql", "key_validation": "not_checked_by_this_endpoint",
        "mcp_tools": [tool.name for tool in app.state.weather_tools],
        "mcp_services": app.state.mcp_manager.status,
    }


@app.post("/api/sessions", status_code=201)
async def create_session(options: SessionOptions | None = None):
    if options and options.user_id:
        from app.api.delivery import require_user
        from starlette.requests import Request
        await require_user(Request({"type":"http", "app":app}), options.user_id)
    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    async with app.state.write_lock:
        await app.state.state_reader.aupdate_state(
            config, {"messages": [], "current_step": "requirement_collection", "user_requirement": {}, "requirement_revision": 0, "requirement_confirmed": False},
            as_node="read_only",
        )
    await app.state.store.aput(("sessions",), session_id, {"user_id": str(options.user_id) if options and options.user_id else None})
    return {"session_id": session_id}


async def read_session(session_id: UUID):
    # 旧匿名学习接口不能绕过正式会话JWT所有权检查。
    from app.full.database import Conversation
    async with app.state.full_db.session() as db:
        if await db.get(Conversation,str(session_id)) is not None:
            raise HTTPException(404, '会话不存在，请使用已登录的正式接口')
    snapshot = await app.state.state_reader.aget_state(
        {"configurable": {"thread_id": str(session_id)}}
    )
    if not snapshot.values:
        raise HTTPException(404, "会话不存在，请先创建会话")
    return snapshot.values


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: UUID):
    return {"session_id": str(session_id), **state_view(await read_session(session_id))}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    settings = Settings()  # .env 保存后下次请求立即读取，无需重启。
    if not settings.model_configured:
        raise HTTPException(503, "请先在项目 .env 填写 DEEPSEEK_API_KEY")
    metrics = RequestMetrics()
    async with app.state.write_lock:
        previous = await read_session(request.session_id)
        model = get_deepseek_llm(settings)
        meta = await app.state.store.aget(("sessions",),str(request.session_id))
        user_id = meta.value.get("user_id") if meta else None
        pref = await app.state.store.aget(("users",user_id,"preferences"),"profile") if user_id else None
        completion = make_completion_tools(model,app.state.mcp_manager,app.state.knowledge,app.state.store,user_id,app.state.remote)
        graph = create_travel_agent(model, app.state.checkpointer, [*app.state.weather_tools,*completion], memory=pref.value if pref else None)
        try:
            result = await asyncio.wait_for(graph.ainvoke(
                {"messages": [HumanMessage(content=request.message)]},
                {"configurable": {"thread_id": str(request.session_id)}, "recursion_limit": 12, "callbacks": [metrics]},
                context=confirmation_context(request.message, previous.get("requirement_revision", 0)),
            ), timeout=120)
        except AuthenticationError:
            metrics.save(PROJECT_ROOT / "logs/request_metrics.jsonl", "authentication_error")
            raise HTTPException(502, "DeepSeek 密钥未通过验证，请检查本机配置") from None
        except RateLimitError:
            metrics.save(PROJECT_ROOT / "logs/request_metrics.jsonl", "rate_limited")
            raise HTTPException(502, "DeepSeek 额度或速率限制，请检查平台账户") from None
        except (APITimeoutError, APIConnectionError, TimeoutError):
            metrics.save(PROJECT_ROOT / "logs/request_metrics.jsonl", "timeout_or_connection_error")
            raise HTTPException(504, "模型请求超时或网络不可达，请稍后重试") from None
        except Exception as exc:
            metrics.save(PROJECT_ROOT / "logs/request_metrics.jsonl", "failed")
            logger.warning("Agent request failed: %s", type(exc).__name__)
            raise HTTPException(502, "模型调用或需求处理失败，请检查配置后重试") from None
    new_messages = result["messages"][len(previous.get("messages", [])):]
    replies = [m for m in new_messages if isinstance(m, AIMessage) and m.content and not m.tool_calls]
    reply = replies[-1].content if replies else "需求处理已结束，请查看当前状态。"
    if any(isinstance(m, ToolMessage) and m.name == 'query_train_tickets' for m in new_messages):
        reply = render_ticket_table(result.get('last_transport_query') or {})
    return {
        "session_id": str(request.session_id), "reply": reply,
        "metrics": metrics.save(PROJECT_ROOT / "logs/request_metrics.jsonl"),
        "tool_calls": [t["name"] for m in new_messages if isinstance(m, AIMessage) for t in m.tool_calls],
        "tool_results": [{"name": m.name, "content": m.content} for m in new_messages if isinstance(m, ToolMessage) and m.name in {"get_city_location", "get_weather_forecast", "query_train_tickets"}],
        **state_view(result),
    }


@app.get("/learn", include_in_schema=False)
async def learn():
    return FileResponse(PROJECT_ROOT / "app/static/learn.html")


@app.get("/travel", include_in_schema=False)
async def travel_page():
    return FileResponse(PROJECT_ROOT / "app/static/travel.html")
