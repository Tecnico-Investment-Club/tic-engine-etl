from random import randint, uniform
from core.config import POSTGRES_CONFIG
from psycopg2.pool import ThreadedConnectionPool
from storage.postgres_db import PostgresRepository
from core.models import Candle
from datetime import datetime,timezone,timedelta

from core.models import Candle
from datetime import datetime, timedelta,timezone


def create_candles(amount:int = 0)->list[Candle]:
    
    if amount != 0:
        time = datetime(2026,11,8, tzinfo=timezone.utc)
        interval = timedelta(minutes=60)
        candles = []
        for i in range(0,amount):
            candle = Candle(
                open = uniform(100,1000),
                close = uniform(100,1000),
                low = uniform(1,99),
                high = uniform(1001,2000),
                vwap = uniform(100,1000),
                volume = uniform(100,1000),
                trade_count = randint(100,1000),
                timestamp = time + (interval * randint(1,100)),
                timeframe = interval,
                broker = "alpaca",
                asset_id="btc-usd"
                )
            candles.append(candle)
        return candles

    
    candles = []
    intervals = [timedelta(minutes=60),timedelta(minutes=45),timedelta(minutes=20),timedelta(minutes=3),timedelta(seconds=45)]
    start = datetime(2026, 1, 1,tzinfo=timezone.utc)
    names = ['btc','eth','doge','apple','microsoft','nvidia','toysrus']


    for name in names:
        
        number_candles = randint(24,832)
        
        for i in range(number_candles):
            
            candle_floats = [uniform(1,4234294) for j in range(6)]
            
            low = min(candle_floats)
            high = max(candle_floats)
            candle_floats.remove(low)
            candle_floats.remove(high)
            
            interval=intervals[randint(0,4)]
            timestamp = (start + (interval * randint(0,7700)))

            candle = Candle(
                low= low,
                high = high,
                open = candle_floats[0],
                close = candle_floats[1],
                vwap = candle_floats[2],
                volume = candle_floats[3],
                trade_count = randint(2,312313),
                timeframe = interval,
                timestamp = timestamp,
                broker = "alpaca",
                asset_id = name
            )
            candles.append(candle)
    return candles

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
    postgres_repo.drop_table()
    postgres_repo._check_table()
    
    candles = create_candles()
    for candle in candles:
        postgres_repo.insert_candle(candle)

    last_candle = postgres_repo.last_candle('btc',timedelta(minutes=20))
    print(last_candle)

    candles_interval = postgres_repo.get_candles('microsoft',timedelta(minutes=60),datetime(2025,11,3 ,tzinfo=timezone.utc),end_time=datetime(2026,5,2, tzinfo=timezone.utc))
    for candle in candles_interval:
        print(candle.timestamp)

if __name__ == "__main__":
    main()



