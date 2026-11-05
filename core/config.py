import json
from dataclasses import dataclass
from pathlib import Path
from datetime import timedelta

@dataclass(frozen=True)
class AssetJob():
    broker: str
    asset_class: str
    timeframe: timedelta
    symbols: dict[str, str]
    lookback_bars: int
    location: str


def load_jobs(path: str = "assets.json") -> list[AssetJob]:
    entries = json.loads(Path(path).read_text())

    for job in entries["asset_jobs"]:
        job["timeframe"] = timedelta(**job["timeframe"])

    return [AssetJob(**job) for job in entries["asset_jobs"]]


