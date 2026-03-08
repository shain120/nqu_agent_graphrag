# agent/tool_schema.py
TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "search_event",
                "description": "從行事曆資料庫查詢活動",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
            {
                "name": "create_calendar_event",
                "description": "建立 Google Calendar 事件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    },
                    "required": ["title", "start", "end"],
                },
            },
        ]
    }
]