import discord
from config import DISCORD_TOKEN
from agent.mcp_agent import run_agent
from collections import OrderedDict
import time

# 記住最近處理過的 message.id（避免同一則訊息重複處理）
_PROCESSED = OrderedDict()
_PROCESSED_TTL_SEC = 60  # 60 秒內相同 message.id 只處理一次
_PROCESSED_MAX = 500

def _seen_before(msg_id: int) -> bool:
    now = time.time()

    # 清掉過期
    expired = [k for k, t in _PROCESSED.items() if now - t > _PROCESSED_TTL_SEC]
    for k in expired:
        _PROCESSED.pop(k, None)

    # 已處理過
    if msg_id in _PROCESSED:
        return True

    _PROCESSED[msg_id] = now

    # 控制大小
    while len(_PROCESSED) > _PROCESSED_MAX:
        _PROCESSED.popitem(last=False)

    return False
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot 已登入為 {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    user_input = message.content.strip()
    if _seen_before(message.id):
        return

    user_input = message.content.strip()
    try:
        reply = await run_agent(user_input)
        if not reply:
            reply = "⚠️ 沒有產生回覆（可能模型沒有回文字）"
    except Exception as e:
        reply = f"❌ 發生錯誤：{type(e).__name__}: {e}"

    await message.channel.send(reply[:2000])

    if len(reply) > 2000:
        for chunk in [reply[i:i+2000] for i in range(0, len(reply), 2000)]:
            await message.channel.send(chunk)
    else:
        await message.channel.send(reply)

client.run(DISCORD_TOKEN)