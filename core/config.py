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

def find_envfile(attribute:str)->str:
    value = os.getenv(attribute)
    if value is not None:
        return value
    else:
        raise ValueError(f"{attribute} is not defined in .env")  ##mypy was complaining that getenv could return None if it's not set


POSTGRES_CONFIG = PostgresConfig(
                    host = find_envfile('POSTGRES_HOST'),
                    port = int(find_envfile('POSTGRES_PORT')),
                    database = find_envfile('POSTGRES_DB'),
                    user = find_envfile('POSTGRES_USER'),
                    password= find_envfile('POSTGRES_PASSWORD'),
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

def find_smallest_timeframe(jobs:list[AssetJob])->timedelta:
    return min(job.timeframe for job in jobs)
