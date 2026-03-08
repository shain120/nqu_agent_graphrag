from pathlib import Path
import pandas as pd
from graphrag.api.query import global_search
from graphrag.config.load_config import load_config

def _load_config(root: Path):
    for kw in ("root", "root_dir"):
        try:
            return load_config(**{kw: root})
        except TypeError:
            continue
    return load_config(root)

def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)

async def run_search(project_root: Path, query: str):
    cfg = _load_config(project_root)
    out = project_root / "output"

    entities = _read_parquet(out / "entities.parquet")
    communities = _read_parquet(out / "communities.parquet")
    reports = _read_parquet(out / "community_reports.parquet")

    resp, ctx = await global_search(
        config=cfg,
        entities=entities,
        communities=communities,
        community_reports=reports,
        community_level=2,
        dynamic_community_selection=True,
        response_type="Multiple Paragraphs",
        query=query,
    )

    return str(resp)