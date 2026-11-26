"""真实 PostgreSQL + 脚本化模型，验证工程行为；不代表真实模型效果。"""
from uuid import uuid4

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage

from app.agents.travel_agent import create_travel_agent
from app.config import Settings
from app.core.checkpointer import open_checkpointer


class ToolFakeModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def model_with_patch(patch):
    return ToolFakeModel(responses=[
        AIMessage(content="", tool_calls=[{"name": "record_requirement_tool", "args": {"updates": patch}, "id": str(uuid4()), "type": "tool_call"}]),
        AIMessage(content="已记录，请补充缺失信息。"),
    ])


@pytest.mark.asyncio
async def test_actual_postgres_restore_and_session_isolation():
    thread = "test-" + str(uuid4())
    config = {"configurable": {"thread_id": thread}}
    settings = Settings()
    try:
        async with open_checkpointer(settings) as saver:
            graph = create_travel_agent(model_with_patch({"destination": "杭州", "travel_days": 3}), saver)
            first = await graph.ainvoke({"messages": [HumanMessage(content="杭州三天")]}, config)
            assert first["user_requirement"] == {"destination": "杭州", "travel_days": 3}
        # 关闭并重建池和 graph，模拟应用重启后的持久化恢复。
        async with open_checkpointer(settings) as saver:
            graph = create_travel_agent(model_with_patch({"departure_city": "上海"}), saver)
            second = await graph.ainvoke({"messages": [HumanMessage(content="从上海出发")]}, config)
            assert second["user_requirement"] == {"destination": "杭州", "travel_days": 3, "departure_city": "上海"}
            assert len(second["messages"]) > len(first["messages"])
            other = await graph.aget_state({"configurable": {"thread_id": "test-" + str(uuid4())}})
            assert not other.values
    finally:
        async with open_checkpointer(settings) as saver:
            await saver.adelete_thread(thread)


def model_with_tool(name, args):
    return ToolFakeModel(responses=[
        AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": str(uuid4()), "type": "tool_call"}]),
        AIMessage(content="本轮已结束。"),
    ])


@pytest.mark.asyncio
async def test_confirmation_and_rollback_persist_across_new_connections():
    from app.core.transitions import ConfirmationContext
    from test_transitions import FULL

    config = {"configurable": {"thread_id": "test-" + str(uuid4())}}
    settings = Settings()
    try:
        async with open_checkpointer(settings) as saver:
            graph = create_travel_agent(model_with_patch(FULL), saver)
            recorded = await graph.ainvoke({"messages": [HumanMessage(content="完整需求")]}, config)
            revision = recorded["requirement_revision"]
            # 即使模型强行产生确认工具调用，没有用户授权也不能改变状态。
            graph = create_travel_agent(model_with_tool("confirm_requirement_tool", {}), saver)
            denied = await graph.ainvoke({"messages": [HumanMessage(content="别确认")]}, config)
            assert denied["requirement_confirmed"] is False
            # 与实际 API 一致：每请求构建模型，避免测试替身复用同一消息 ID 被 reducer 去重。
            graph = create_travel_agent(model_with_tool("confirm_requirement_tool", {}), saver)
            confirmed = await graph.ainvoke({"messages": [HumanMessage(content="确认")]}, config, context=ConfirmationContext(revision))
            assert confirmed["current_step"] == "transport_planning"
            assert confirmed["requirement_confirmed"] is True
            graph = create_travel_agent(model_with_patch({"destination": "苏州"}), saver)
            changed = await graph.ainvoke({"messages": [HumanMessage(content="改成苏州")]}, config)
            assert changed["requirement_confirmed"] is False
            assert changed["current_step"] == "requirement_collection"
        async with open_checkpointer(settings) as saver:
            graph = create_travel_agent(model_with_tool("confirm_requirement_tool", {}), saver)
            restored = (await graph.aget_state(config)).values
            assert restored["user_requirement"]["destination"] == "苏州"
            assert restored["user_requirement"]["departure_city"] == "上海"
            assert restored["confirmed_revision"] is None
    finally:
        async with open_checkpointer(settings) as saver:
            await saver.adelete_thread(config["configurable"]["thread_id"])
