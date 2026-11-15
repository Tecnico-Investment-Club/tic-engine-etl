from storage.postgres_db import PostgresRepository
from core.config import AssetJob,load_jobs
from datetime import datetime,timedelta,timezone

class etlEngine():
    def __init__(self,alpaca_client):
        self.jobs = load_jobs()
        self.repo = PostgresRepository()
   

    

    def _get_next_fecth(self)->dict[tuple[str,timedelta],datetime]:
        """for each symbol and timeframe search the database for last candle, return where to start getting new candles, if no candle go to the max lookback bars"""
        next_fetch: dict [tuple[str,timedelta],datetime] = {}

        for job in self.jobs:
            for asset_id in job.symbols:
                last_stored = self.repo.get_last_candle(asset_id,job.timeframe)
                if last_stored == None:
                    start = datetime.now(timezone.utc) - (job.timeframe * (job.lookback_bars + 1)) ###if start is for example 17,23 and llookback is 4 alpaca doesnt give the 13-14 bar becuase start would be in 13,23. so we go back one extra to ensure proper lookback
                    next_fetch[asset_id,job.timeframe] = start
                    
                else:
                    next_fetch[asset_id,job.timeframe] = last_stored.timestamp + job.timeframe
        return next_fetch