import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # calendar_bot/
EVENTS_PATH = BASE_DIR / "data" / "events.json"

with EVENTS_PATH.open(encoding="utf-8") as f:
    EVENTS = json.load(f)

async def search_event(query: str):
    results = [e for e in EVENTS if query in e.get("title", "")]
    return {"events": results}