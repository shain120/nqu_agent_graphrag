# -*- coding: utf-8 -*-
"""
global_search (新版 API 相容版，無 nodes 參數)

需求：
- settings.yaml 必須在 root 下
- output 下需有 entities.parquet、communities.parquet、community_reports.parquet

用法：
  python -m global_search --query "請列出三大主題，各主題兩行說明"
  python -m global_search --root /path/to/project --query "..."
"""

import argparse
import asyncio
from pathlib import Path
import pandas as pd

from graphrag.api.query import global_search
from graphrag.config.load_config import load_config


def _load_config(root: Path):
    """兼容不同版本 load_config 的參數寫法"""
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

    # 印出 chat / embedding 設定，確認是 Ollama / HF
    for key in ("default_chat_model", "default_embedding_model"):
        try:
            print(f"[config] {key}:", cfg.models[key])
        except Exception:
            pass

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


def _parse_args():
    ap = argparse.ArgumentParser(description="Run GraphRAG Global Search")
    ap.add_argument("--root", type=Path, default=Path(__file__).parent,
                    help="專案根目錄（含 settings.yaml / output）")
    ap.add_argument("--query", required=True, help="查詢內容")
    ap.add_argument("--level", type=int, default=2, help="community_level（可為 None）")
    ap.add_argument("--no-dynamic", action="store_true", help="關閉動態社群選擇")
    ap.add_argument("--response-type", default="Multiple Paragraphs",
                    help="回應型態（如 'Multiple Paragraphs', 'Bulleted List'）")
    return ap.parse_args()


def main():
    args = _parse_args()
    root = args.root.resolve()
    if not (root / "settings.yaml").exists():
        raise FileNotFoundError(f"{root}/settings.yaml 不存在")

    async def _run():
        resp, ctx = await run_global_search_once(
            root, args.query,
            community_level=args.level,
            dynamic=not args.no_dynamic,
            response_type=args.response_type,
        )
        print("\n=== 回答 ===\n", resp)
        print("\n=== 上下文使用量 ===")
        for k in ["reports", "entities", "relationships", "claims", "sources"]:
            print(f"{k:14}", len(ctx.get(k, [])))

    asyncio.run(_run())


if __name__ == "__main__":
    main()

