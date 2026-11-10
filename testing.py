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
    intervals = [timedelta(minutes=60),timedelta(seconds=60),timedelta(days=1)]
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
            
            interval=intervals[randint(0,len(intervals)-1)]
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



def random_datetimes():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    start = base + timedelta(hours=randint(0, 5000))
    end = start + timedelta(hours=randint(1, 2000))
    return start, end


def main():
    postgres_repo = PostgresRepository()
    postgres_repo.kill_table()
    print("all tables dropped")

    
    postgres_repo = PostgresRepository()
    print("tables created")

    candles = create_candles()
    for candle in candles:
        postgres_repo.insert_candles_new(candle)
    print("all candles created")

    start, end = random_datetimes()
    candles = postgres_repo.find_candle_interval_new("microsoft",timedelta(minutes=60),start,end)
    for candle in candles:
        print(candle.volume)
    print("candles in interval found")
    

    candle = postgres_repo.find_last_candle_new("doge",timedelta(seconds=60))
    print(candle.vwap)
    print("last candle foudn")

    
if __name__ == "__main__":
    main()



