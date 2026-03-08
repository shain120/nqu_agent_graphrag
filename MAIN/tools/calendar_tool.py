# tools/calendar_tool.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import TIMEZONE

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 來源標記（用於防重複）
BOT_SOURCE_TAG = "NQU_agent"

BASE_DIR = Path(__file__).resolve().parents[1]  # calendar_bot/
TOKEN_PATH = BASE_DIR / "token.json"
CREDS_PATH = BASE_DIR / "credentials.json"

# 台灣固定 UTC+8，不用 zoneinfo / tzdata
TAIPEI_TZ = timezone(timedelta(hours=8), name="Asia/Taipei")


def get_service():
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                raise FileNotFoundError(f"credentials.json 不存在：{CREDS_PATH}")

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)


def _parse_dt(s: str) -> datetime:
    """
    解析 ISO datetime，例如 2026-03-04T00:00:00
    沒有 tzinfo 就補台北時區（UTC+8）
    """
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TAIPEI_TZ)
    return dt


def _to_utc_rfc3339(dt: datetime) -> str:
    """
    Google Calendar list 的 timeMin/timeMax 建議用 UTC RFC3339（...Z）
    """
    dt_utc = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _get_event_source_tag(ev: dict) -> str | None:
    return (
        ev.get("extendedProperties", {})
        .get("private", {})
        .get("source")
    )


def find_duplicate_event(service, calendar_id: str, title: str, time_min: str, time_max: str) -> dict | None:
    """
    在 time_min ~ time_max 內找同標題 + 同來源標記的事件
    """
    resp = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
        maxResults=100,
    ).execute()

    for ev in resp.get("items", []):
        if ev.get("summary") != title:
            continue
        if _get_event_source_tag(ev) == BOT_SOURCE_TAG:
            return ev

    return None


def create_calendar_event(title: str, start: str, end: str, calendar_id: str = "primary"):
    """
    建立 Google Calendar 事件（含防重複）
    - 全天事件：用 date，並把 end.date 修成 exclusive（+1 天）
    - 非全天事件：用 dateTime，確保 end > start
    """
    service = get_service()

    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)

    is_all_day_like = (
        start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0
        and end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0
    )

    if is_all_day_like:
        start_date = start_dt.date()
        end_date = end_dt.date()

        # Google end.date 是 exclusive
        if end_date <= start_date:
            end_date = start_date + timedelta(days=1)
        else:
            # 你資料通常代表「最後一天也要算進去」
            end_date = end_date + timedelta(days=1)

        # 防重複：用 start_date 00:00 到 end_date 00:00（exclusive）
        time_min = _to_utc_rfc3339(datetime.combine(start_date, datetime.min.time(), tzinfo=TAIPEI_TZ))
        time_max = _to_utc_rfc3339(datetime.combine(end_date, datetime.min.time(), tzinfo=TAIPEI_TZ))

        dup = find_duplicate_event(service, calendar_id, title, time_min, time_max)
        if dup:
            return {
                "status": "exists",
                "message": f"{title} 已存在於行事曆（已略過建立）",
                "eventId": dup.get("id"),
                "htmlLink": dup.get("htmlLink"),
                "summary": dup.get("summary"),
                "start": dup.get("start"),
                "end": dup.get("end"),
                "calendarId": calendar_id,
            }

        body = {
            "summary": title,
            "start": {"date": start_date.isoformat()},
            "end": {"date": end_date.isoformat()},
            "extendedProperties": {"private": {"source": BOT_SOURCE_TAG}},
        }

    else:
        if end_dt <= start_dt:
            end_dt = start_dt + timedelta(hours=1)

        time_min = _to_utc_rfc3339(start_dt)
        time_max = _to_utc_rfc3339(end_dt)

        dup = find_duplicate_event(service, calendar_id, title, time_min, time_max)
        if dup:
            return {
                "status": "exists",
                "message": f"{title} 已存在於行事曆（已略過建立）",
                "eventId": dup.get("id"),
                "htmlLink": dup.get("htmlLink"),
                "summary": dup.get("summary"),
                "start": dup.get("start"),
                "end": dup.get("end"),
                "calendarId": calendar_id,
            }

        body = {
            "summary": title,
            "start": {"dateTime": start_dt.replace(microsecond=0).isoformat(), "timeZone": TIMEZONE},
            "end": {"dateTime": end_dt.replace(microsecond=0).isoformat(), "timeZone": TIMEZONE},
            "extendedProperties": {"private": {"source": BOT_SOURCE_TAG}},
        }

    created = service.events().insert(calendarId=calendar_id, body=body).execute()

    return {
        "status": "success",
        "message": f"{title} 已加入行事曆",
        "eventId": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "summary": created.get("summary"),
        "start": created.get("start"),
        "end": created.get("end"),
        "calendarId": calendar_id,
    }