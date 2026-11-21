from core.config import load_jobs,find_smallest_timeframe
from datetime import datetime,timedelta,timezone
from core.models import Candle
import json
from time import sleep
import logging

logger = logging.getLogger(__name__)


class etlEngine():
    def __init__(self,alpaca_client, repo):
        self.jobs = load_jobs()
        self.repo = repo
        self.alpaca_client = alpaca_client
    
    

    def _get_next_fetch(self)->dict[tuple[str,timedelta],datetime]:
        """for each symbol and timeframe search the database for last candle, return where to start getting new candles, if no candle go to the max lookback bars"""
        next_fetch: dict [tuple[str,timedelta],datetime] = {}

        for job in self.jobs:
            for asset_id in job.symbols:
                last_stored = self.repo.get_last_candle(asset_id,job.timeframe)
                if last_stored is None:
                    start = datetime.now(timezone.utc) - (job.timeframe * (job.lookback_bars + 1)) ###if start is for example 17,23 and llookback is 4 alpaca doesnt give the 13-14 bar becuase start would be in 13,23. so we go back one extra to ensure proper lookback
                    next_fetch[asset_id,job.timeframe] = start
                    
                else:
                    max_lookback_allowed = datetime.now(timezone.utc) - job.timeframe * (job.lookback_bars + 1)
                    next_fetch[asset_id,job.timeframe] = max(last_stored.timestamp + job.timeframe, max_lookback_allowed)
        return next_fetch

    def _fetch_missing(self) -> list[Candle]:
        next_fetch = self._get_next_fetch()
        all_candles = []

        for (asset_id, timeframe), start in next_fetch.items():
            candles = self.alpaca_client.fetch_candles(
                asset_id=asset_id,
                start=start,
                timeframe=timeframe
            )

            all_candles.extend(candles)

        return all_candles

    def run_cycle(self) -> dict[tuple[str, timedelta], list[Candle]]:
        candles = self._fetch_missing()

        now = datetime.now(timezone.utc)

        for candle in candles:
            if candle.endtime <= now:
                self.repo.insert_candle(candle)

        lookbacks = {}

        for job in self.jobs:
            for asset_id in job.symbols:
                lookbacks[asset_id, job.timeframe] = self.repo.get_lookback(
                    asset_id,
                    job.timeframe,
                    job.lookback_bars
                )

        return lookbacks


    def output(self,lookbacks:dict[tuple[str,timedelta],list[Candle]])->None:
        items = []

        for (asset_id,timeframe), candles in lookbacks.items():
            candle_dicts = []
            for candle in candles:
                candle_dicts.append({
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "close": candle.close,
                    "high": candle.high,
                    "low": candle.low,
                    "volume": candle.volume,
                    "trade_count": candle.trade_count,
                    "vwap": candle.vwap
                })

            items.append({
                "asset_id": asset_id,
                "timeframe_seconds": int(timeframe.total_seconds()),
                "lookback": len(candle_dicts),
                "candles": candle_dicts
            })

        data = {"lookback_time": datetime.now(timezone.utc).isoformat(),
                "items": items
                }

        with open("lookback_file.json","w") as file:
            json.dump(data,file,indent=2)



    
    @staticmethod
    def seconds_until_next_cycle(smallest_timeframe:timedelta,wait_after_timeframe:timedelta)->int:
        now = datetime.now(timezone.utc)
        now = now.replace(minute=0,second=0,microsecond=0)
        next_time = now + smallest_timeframe + wait_after_timeframe
        interval =next_time -  datetime.now(timezone.utc) 
        return int(interval.total_seconds())


    def run(self)->None:

        logger.info("starting warmup run")
        lookback = self.run_cycle()
        self.output(lookback)
        
        
        smallest_timeframe = find_smallest_timeframe(self.jobs)
        WAIT_AFTER_TIMEFRAME = timedelta(minutes=1)
        wait_seconds = self.seconds_until_next_cycle(smallest_timeframe,WAIT_AFTER_TIMEFRAME)

        logger.info(f"warmup completed sleeping for {wait_seconds} seconds ")
        sleep(wait_seconds)
        
        while True:
            try:
                lookback = self.run_cycle()
                self.output(lookback)
                logger.info("ran cycle sucefully")
            except Exception:
                logger.exception("faiiled to run cycle")
                pass
            wait_seconds = self.seconds_until_next_cycle(smallest_timeframe,WAIT_AFTER_TIMEFRAME)
            logger.info(f"slepping for {wait_seconds}")
            sleep(wait_seconds)
