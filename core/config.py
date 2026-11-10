import json
from dataclasses import dataclass
from pathlib import Path
from datetime import timedelta
import os



@dataclass(frozen=True,kw_only=True)
class PostgresConfig():
    host: str
    port: int
    database: str
    user: str
    password: str
    minimum_connections: int
    maximum_connections: int


POSTGRES_CONFIG = PostgresConfig(
                    host = os.getenv('POSTGRES_HOST'),
                    port = int(os.getenv('POSTGRES_PORT')),
                    database = os.getenv('POSTGRES_DB'),
                    user = os.getenv('POSTGRES_USER'),
                    password= os.getenv('POSTGRES_PASSWORD'),
                    minimum_connections= 0,
                    maximum_connections= 10
)


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


