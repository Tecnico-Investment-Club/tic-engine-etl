#create pool object with info from config
from core.config import POSTGRES_CONFIG
from psycopg2.pool import ThreadedConnectionPool
from storage.postgres_db import PostgresRepository
from core.models import Candle
from datetime import datetime,timezone,timedelta


def main():
    connection_pool = ThreadedConnectionPool(
                            host=POSTGRES_CONFIG.host,
                            port=POSTGRES_CONFIG.port ,
                            database=POSTGRES_CONFIG.database,
                            user=POSTGRES_CONFIG.user,
                            password=POSTGRES_CONFIG.password,
                            minconn=POSTGRES_CONFIG.minimum_connections,
                            maxconn=POSTGRES_CONFIG.maximum_connections,
    )

    postgres_repo = PostgresRepository(connection_pool)
    candle = Candle(
    open=2.0,
    close=3.0,
    high=7.0,
    low=1.0,
    asset_id="ffff",
    broker="ihfawiuhf",
    volume=133.974,
    trade_count=40,
    timestamp=datetime(2026, 11, 9, 16, 30, 0, tzinfo=timezone.utc),
    timeframe=timedelta(minutes=5),
    vwap=5.7,
        )
    postgres_repo.drop_table()
    postgres_repo._check_table()
    postgres_repo.insert_candle(candle)

if __name__ == "__main__":
    main()


