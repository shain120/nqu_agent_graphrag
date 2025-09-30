import nest_asyncio
import discord 
from pathlib import Path
import asyncio

from graphrag.api.query import global_search
from graphrag.config.load_config import load_config
import pandas as pd

nest_asyncio.apply()

def _load_config(root: Path):
    for kw in ("root", "root_dir"):
        try:
            return load_config(**{kw: root})
        except TypeError:
            continue
    return load_config(root)

def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"缺檔：{path}")
    return pd.read_parquet(path)

async def run_global_search_once(
    root: Path, query: str,
    community_level: int | None = 2,
    dynamic: bool = True,
    response_type: str = "Multiple Paragraphs",
):
    cfg = _load_config(root)
    out = root / "output"

    entities = _read_parquet(out / "entities.parquet")
    communities = _read_parquet(out / "communities.parquet")
    reports = _read_parquet(out / "community_reports.parquet")

    resp, ctx = await global_search(
        config=cfg,
        entities=entities,
        communities=communities,
        community_reports=reports,
        community_level=community_level,
        dynamic_community_selection=dynamic,
        response_type=response_type,
        query=query,
    )
    return resp, ctx

### Discord bot
discord_bot_token = "put your discord-api"
project_root = Path("/home/user/Downloads/SH/graphrag/graphrag_ollama")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot 已登入為 {client.user}")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.type != discord.MessageType.default:
        return
    if message.author.bot:
        return

    user_input = message.content.strip()
    if not user_input:
        return

    try:
        resp, ctx = await run_global_search_once(
            project_root,
            query=user_input,
            community_level=2,
            dynamic=True,
            response_type="Multiple Paragraphs",
        )
        response_content = str(resp)
    except Exception as e:
        response_content = f"⚠️ 發生錯誤: {e}"

    # Discord 長度限制處理
    if len(response_content) > 2000:
        for chunk in [response_content[i:i+2000] for i in range(0, len(response_content), 2000)]:
            await message.channel.send(chunk)
    else:
        await message.channel.send(response_content)

client.run(discord_bot_token)