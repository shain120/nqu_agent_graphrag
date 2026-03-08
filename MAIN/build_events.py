import json
from utils.pdf_reader import read_pdf_text
from utils.calendar_parser import parse_events
from config import PDF_PATH

text = read_pdf_text(PDF_PATH)
events = parse_events(text)

with open("data/events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print("✅ 已建立 events.json")