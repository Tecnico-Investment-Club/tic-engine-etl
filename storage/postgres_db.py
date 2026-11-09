import psycopg2
from core.models import Candle
from contextlib import contextmanager
from datetime import timedelta


#remember to convert timeframe into seconds and then into timedelta


class PostgresRepository():
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self._check_table()


    @contextmanager
    def _get_connection(self):
        database_connection = self.connection_pool.getconn()
        try:
            yield database_connection
        finally:
            self.connection_pool.putconn(database_connection)
    @staticmethod
    def convert_timedelta_seconds(timeframe:timedelta)->Int:
        return int(timeframe.total_seconds())

    @staticmethod
    def convert_seconds_seconds(seconds_quantity:int)->timedelta:
        return timedelta(seconds=seconds_quantity)

    
    def drop_table(self):
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""DROP TABLE IF EXISTS candle""")

                
    def _check_table(self):
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    CREATE_TABLE_CANDLE = """
                        CREATE TABLE IF NOT EXISTS candle(
                            open FLOAT8 NOT NUll,
                            close FLOAT8 NOT NULL,
                            high FLOAT8 NOT NULL,
                            low FLOAT8 NOT NULL,
                            asset_id TEXT NOT NULL,
                            volume FLOAT8 NOT NULL,
                            trade_count INT NOT NULL,
                            timestamp TIMESTAMPTZ NOT NULL,
                            timeframe INT NOT NULL,
                            PRIMARY KEY(asset_id,timestamp,timeframe)  
                        );
                        """
                    cursor.execute(CREATE_TABLE_CANDLE)

    def insert_candle(self,candle:Candle):
        open = candle.open
        close = candle.close
        high = candle.close
        low = candle.low
        asset_id = candle.asset_id
        volume = candle.volume
        trade_count = candle.trade_count
        timestamp = candle.timestamp
        timeframe = self.convert_timedelta_seconds(candle.timeframe)
        values = (open,close,high,low,asset_id,volume,trade_count,timestamp,timeframe,)
        INSERT_CANDLE = """
                        INSERT INTO candle
                        (
                        open,
                        close,
                        high,
                        low,
                        asset_id,
                        volume,
                        trade_count,
                        timestamp,
                        timeframe
                        ) 
                        VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (asset_id,timestamp,timeframe) DO NOTHING;
                        """
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(INSERT_CANDLE,values)
