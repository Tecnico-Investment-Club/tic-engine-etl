from psycopg2.pool import ThreadedConnectionPool
from core.models import Candle
from contextlib import contextmanager
from datetime import timedelta,datetime,timezone
from core.config import POSTGRES_CONFIG


class PostgresRepository():
    def __init__(self):
        
        self.start_repo()


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
                            vwap FLOAT8 NOT NULL,
                            PRIMARY KEY(asset_id,timestamp,timeframe)  
                        );
                        """
                    cursor.execute(CREATE_TABLE_CANDLE)
    
    def insert_candle(self,candle:Candle):
        open = candle.open
        close = candle.close
        high = candle.high
        low = candle.low
        asset_id = candle.asset_id
        volume = candle.volume
        trade_count = candle.trade_count
        timestamp = candle.timestamp
        timeframe = self.convert_timedelta_seconds(candle.timeframe)
        vwap = candle.vwap
        values = (open,close,high,low,asset_id,volume,trade_count,timestamp,timeframe,vwap)
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
                        timeframe,
                        vwap
                        ) 
                        VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (asset_id,timestamp,timeframe) DO NOTHING;
                        """
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(INSERT_CANDLE,values)


    #make first to find one stimestamp
    ## then make to find on interval

    def find_candle(self,asset_id:str,timestamp:datetime,timeframe:timedelta) ->Candle:
        PROMPT="""SELECT * FROM candle WHERE timestamp = %s AND asset_id = %s AND timeframe = %s"""
        timeframe = self.convert_timedelta_seconds(timeframe)
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(PROMPT,(timestamp,asset_id,timeframe))
                    candle = cursor.fetchall()
        return candle



    #turn them into candle objects , make method for that
    def get_candles(self,asset_id:str,timeframe:timedelta,start_time:datetime,end_time:datetime)->List[Candle]:
        PROMPT = """SELECT * FROM candle WHERE asset_id = %s AND timeframe = %s AND timestamp >= %s AND timestamp <= %s;"""
        timeframe = self.convert_timedelta_seconds(timeframe)
        parameters =(asset_id,timeframe,start_time,end_time)
        
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(PROMPT,parameters)
                    candles_tupples = cursor.fetchall()
        candles = []
        for candle in candles_tupples:
            candles.append(self.tuple_to_candle(candle))
        return candles

    def last_candles(self, asset_id:str,timeframe:timedelta,number_candles:int)->List[Candle]:
        PROMPT = """SELECT * FROM candle WHERE asset_id = %s AND timeframe = %s ORDER BY timestamp DESC LIMIT %s;"""
        timeframe = self.convert_timedelta_seconds(timeframe)
        parameters = (asset_id,timeframe,number_candles)
        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursos:
                    cursos.execute(PROMPT,parameters)
                    candles_tupples = cursos.fetchall()
        candles = []
        for candle in candles_tupples:
            candles.append(self.tuple_to_candle(candle))
        return candles



    @staticmethod
    def tuple_to_candle(candle_info: tuple) -> Candle:
        
        if candle_info:
            return Candle(
                open=candle_info[0],
                close=candle_info[1],
                high=candle_info[2],
                low=candle_info[3],
                asset_id=candle_info[4],
                broker="placeholder",  
                volume=candle_info[5],
                trade_count=candle_info[6],
                timestamp=candle_info[7].astimezone(timezone.utc),
                timeframe=PostgresRepository.convert_seconds_seconds(candle_info[8]),
                vwap=candle_info[9],
                )
        else:
            return None


    def last_candle(self,asset_id:str,timeframe:timedelta)->Candle:
        PROMPT = """SELECT * FROM candle WHERE asset_id = %s AND timeframe = %s ORDER BY timestamp DESC LIMIT 1;"""
        timeframe = self.convert_timedelta_seconds(timeframe)
        parameters = (asset_id,timeframe)

        with self._get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(PROMPT,parameters)
                    candle_tuple = cursor.fetchone()
        return self.tuple_to_candle(candle_tuple)


    #this shouild beocme init
    def start_repo(self):
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

    
    TIMEFRAME_TO_TABLES = {
        timedelta(minutes= 60): "candle_1hour",
        timedelta(days=1): "candle_1day",
        timedelta(minutes=1):"candles_1minute"
    }

    def _check_tables(self):
        PROMPT = """CREATE TABLE IF NOT EXISTS {table_name}(
                                    open FLOAT8 NOT NUll,
                                    close FLOAT8 NOT NULL,
                                    high FLOAT8 NOT NULL,
                                    low FLOAT8 NOT NULL,
                                    asset_id TEXT NOT NULL,
                                    volume FLOAT8 NOT NULL,
                                    trade_count INT NOT NULL,
                                    timestamp TIMESTAMPTZ NOT NULL,
                                    vwap FLOAT8 NOT NULL,
                                    PRIMARY KEY(asset_id,timestamp)  
                                );
                                """

        for  table in self.TIMEFRAME_TO_TABLES.values():
            with self._get_connection() as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(PROMPT.format(table_name=table))