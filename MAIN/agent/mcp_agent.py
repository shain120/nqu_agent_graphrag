# agent/mcp_agent.py
from __future__ import annotations
import asyncio

from agent.gemini_client import build_model, send_message_async
from agent.tool_schema import TOOLS_SCHEMA
from agent.prompts import SYSTEM_PROMPT

from tools.search_event_tool import search_event
from tools.calendar_tool import create_calendar_event

model = build_model(TOOLS_SCHEMA)

async def run_agent(user_input: str) -> str:
    chat = model.start_chat()

    # 先給系統規則（用第一句塞進去）
    response = await send_message_async(chat, SYSTEM_PROMPT + "\n\n使用者：" + user_input)

    while True:
        part = response.candidates[0].content.parts[0]

        # 不是 function call → 直接回覆
        if not hasattr(part, "function_call") or part.function_call is None:
            return getattr(part, "text", "") or ""

        fn = part.function_call.name
        args = part.function_call.args or {}

        if not args:
            response = await send_message_async(chat, f"工具 {fn} 需要參數，但你沒有提供，請補齊參數。")
            continue

        # Tool Router
        if fn == "search_event":
            result = await search_event(args.get("query", ""))

        elif fn == "create_calendar_event":
            # Google Calendar API 是同步 I/O → 一樣丟 thread，避免卡住
            try:
                result = await asyncio.to_thread(
                    create_calendar_event,
                    args.get("title"),
                    args.get("start"),
                    args.get("end"),
                )
            except Exception as e:
                # ✅ 一旦工具錯誤，立刻回覆並結束，不再讓模型重試
                return f"❌ 發生錯誤：{type(e).__name__}: {e}"

            # success / exists 都直接 return，避免又丟回 Gemini 造成重試
            if result.get("status") == "success":
                return (
                    "✅ 已新增到 Google Calendar\n"
                    f"📌 標題：{result.get('summary')}\n"
                    f"🕒 開始：{result.get('start')}\n"
                    f"🕒 結束：{result.get('end')}\n"
                    f"🔗 事件連結：{result.get('htmlLink')}"
                )
            if result.get("status") == "exists":
                return (
                    "⚠️ 行事曆已有相同事件，已略過新增\n"
                    f"📌 標題：{result.get('summary')}\n"
                    f"🔗 事件連結：{result.get('htmlLink')}"
                )

            return f"❌ 建立事件失敗：{result}"

        # 把 tool result 回給 Gemini（也要 async thread）
        response = await send_message_async(
            chat,
            {"function_response": {"name": fn, "response": result}},
        )