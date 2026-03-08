# agent/gemini_client.py
from __future__ import annotations
import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

# 注意：tools/function_declarations 你可以照你原本的放
def build_model(tools_schema: list[dict], model_name: str = "gemini-2.5-flash"):
    return genai.GenerativeModel(model_name=model_name, tools=tools_schema)

async def send_message_async(chat, msg):
    """
    把同步的 chat.send_message 丟到 thread 跑，避免卡住 Discord event loop
    """
    return await asyncio.to_thread(chat.send_message, msg)