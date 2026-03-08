import re
from datetime import datetime
from config import YEAR

MONTH_MAP = {
    "二月": 2,
    "三月": 3,
    "四月": 4,
    "五月": 5,
    "六月": 6,
    "七月": 7,
}

def parse_events(text: str):

    events = []
    current_month = None
    last_day_seen = 0

    lines = text.split("\n")

    for line in lines:

        # 🔹 1️⃣ 偵測月份標題
        for month_name, month_number in MONTH_MAP.items():
            if month_name in line:
                current_month = month_number
                last_day_seen = 0

        if not current_month:
            continue

        # 🔹 2️⃣ 區間事件
        range_pattern = r"(\d+)日至(\d+)日\s*(.+)"
        match_range = re.search(range_pattern, line)

        if match_range:
            start_day, end_day, title = match_range.groups()

            start_day = int(start_day)
            end_day = int(end_day)

            # 若日期倒退，表示跨月
            if start_day < last_day_seen:
                current_month += 1

            last_day_seen = start_day

            try:
                start_date = datetime(YEAR, current_month, start_day)
                end_date = datetime(YEAR, current_month, end_day)
            except ValueError:
                continue  # 略過非法日期

            events.append({
                "title": title.strip(),
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            })

            continue

        # 🔹 3️⃣ 單日事件
        single_pattern = r"(\d+)日\s*(.+)"
        match_single = re.search(single_pattern, line)

        if match_single:
            day, title = match_single.groups()
            day = int(day)

            # 日期倒退 → 跨月
            if day < last_day_seen:
                current_month += 1

            last_day_seen = day

            try:
                date = datetime(YEAR, current_month, day)
            except ValueError:
                continue

            events.append({
                "title": title.strip(),
                "start": date.isoformat(),
                "end": date.isoformat()
            })

    return events