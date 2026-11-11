from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import sql
from core.models import Candle
from contextlib import contextmanager
from datetime import timedelta,datetime,timezone
from core.config import POSTGRES_CONFIG



class PostgresRepository():
    
    TIMEFRAME_TO_TABLES = {
        timedelta(minutes= 60): "candle_1h",
        timedelta(days=1): "candle_1d",
    }


    
    def __init__(self):
        self.start_repo()



    def start_repo(self)->None:
        self.connection_pool = ThreadedConnectionPool(
                                    host=POSTGRES_CONFIG.host,
                                    port=POSTGRES_CONFIG.port ,
                                    database=POSTGRES_CONFIG.database,
                                    user=POSTGRES_CONFIG.user,
                                    password=POSTGRES_CONFIG.password,
                                    minconn=POSTGRES_CONFIG.minimum_connections,
                                    maxconn=POSTGRES_CONFIG.maximum_connections,
            )
        self._check_tables()


    def _check_tables(self)->None:
        CREATE_TABLES = sql.SQL("""CREATE TABLE IF NOT EXISTS {table_name}(
                                    open FLOAT8 NOT NULL,
                                    close FLOAT8 NOT NULL,
                                    high FLOAT8 NOT NULL,
                                    low FLOAT8 NOT NULL,
                                    asset_id TEXT NOT NULL,
                                    volume FLOAT8 NOT NULL,
                                    trade_count INT NOT NULL,
                                    timestamp TIMESTAMPTZ NOT NULL,
                                    vwap FLOAT8 NOT NULL,
                                    broker TEXT NOT NULL,
                                    PRIMARY KEY(asset_id,timestamp)  
                                ); """)

        for  table in self.TIMEFRAME_TO_TABLES.values():
            with self._get_connection() as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(CREATE_TABLES.format(table_name=sql.Identifier(table)))


    def insert_candle(self,candle : Candle)->None:
        INSERT_CANDLES =sql.SQL( """INSERT INTO {table_name}(
                                open,
                                close,
                                high,
                                low,
                                asset_id,
                                volume,
                                trade_count,
                                timestamp,
                                vwap,
                                broker
                                ) 
                                VALUES (
                                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                ON CONFLICT (asset_id,timestamp) DO NOTHING; """)
        
        parameters = (candle.open,candle.close,candle.high,candle.low,candle.asset_id,candle.volume,candle.trade_count,candle.timestamp,candle.vwap,candle.broker)
        table_name = self._timeframe_to_tables(candle.timeframe)
        
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(INSERT_CANDLES.format(table_name=sql.Identifier(table_name)),parameters)


    def get_candles_interval(self,asset_id:str,timeframe:timedelta,start_time:datetime,end_time:datetime)->list[Candle]:
        """gives oldest first"""
        FIND_CANDLES = sql.SQL("""SELECT * FROM {table_name} WHERE asset_id = %s AND timestamp>= %s AND TIMESTAMP<=%s ORDER BY timestamp ASC""")
        
        parameters = (asset_id,start_time,end_time)
        table_name = self._timeframe_to_tables(timeframe)

        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(FIND_CANDLES.format(table_name=sql.Identifier(table_name)),parameters)
                    candles_tuples = cursor.fetchall()
        
        candles = []
        for candle in candles_tuples:
            candles.append(self.tuple_to_candle(candle,timeframe))
        return candles


    def get_last_candle(self,asset_id:str,timeframe:timedelta)->Candle | None:
        GET_LAST_CANDLES = sql.SQL("""SELECT * FROM {table_name} WHERE asset_id=%s ORDER BY timestamp DESC LIMIT 1""")

        parameters = (asset_id,)
        table_name = self._timeframe_to_tables(timeframe)

        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_LAST_CANDLES.format(table_name=sql.Identifier(table_name)),parameters)
                    candle= cursor.fetchone()
        
        return self.tuple_to_candle(candle,timeframe)


    def get_lookback(self,asset_id:str,timeframe:timedelta,number_candles:int)->list[Candle]:
        """oldest first"""
        GET_LOOKBACK = sql.SQL("""SELECT * FROM {table_name} WHERE asset_id=%s ORDER BY timestamp DESC LIMIT %s""")

        parameters = (asset_id,number_candles)
        table_name = self._timeframe_to_tables(timeframe)

        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_LOOKBACK.format(table_name=sql.Identifier(table_name)),parameters)
                    candles_tupples = cursor.fetchall()

        candles = []
        for candle in candles_tupples:
            candles.append(self.tuple_to_candle(candle,timeframe))
        candles.reverse()
        return candles



    @contextmanager
    def _get_connection(self):
        database_connection = self.connection_pool.getconn()
        try:
            yield database_connection
        finally:
            self.connection_pool.putconn(database_connection)


    @staticmethod
    def tuple_to_candle(candle_info: tuple | None, timeframe: timedelta) -> Candle | None:
        if candle_info:
            return Candle(
            open = candle_info[0],
            close = candle_info[1],
            high = candle_info[2],
            low = candle_info[3],
            asset_id = candle_info[4],
            volume = candle_info[5],
            trade_count = candle_info[6],
            timestamp = candle_info[7].astimezone(timezone.utc),
            timeframe = timeframe,
            vwap = candle_info[8],
            broker = candle_info[9]
            )
        else:
            return None


    def _timeframe_to_tables(self,timeframe:timedelta)->str:
        if timeframe in self.TIMEFRAME_TO_TABLES:
            return self.TIMEFRAME_TO_TABLES[timeframe]
        else:
            raise ValueError(f"no table for timeframe = {timeframe}")


    def close(self)->None:
        self.connection_pool.closeall()
    