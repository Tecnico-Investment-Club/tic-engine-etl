from dataclasses import dataclass
from datetime import datetime,timedelta


@dataclass(frozen=True,slots=True)
class Candle():
    open: float
    close: float
    high:float
    low:float
    asset_id:str
    broker:str
    volume:float
    trade_count:int
    timestamp:datetime
    timeframe:timedelta
    vwap:float

    @property
    def endtime(self) -> datetime:
        return self.timestamp+self.timeframe
    
    def __post_init__(self) ->None:
        if (
            any(value < 0 for value in (
                self.open,
                self.close,
                self.high,
                self.low,
                self.trade_count,
                self.volume,
                self.vwap,
            ))
            or self.high < self.low
        ):
            raise ValueError("failed to build candle")
        """FIXME:Verify the attributes' format, verify that open and close are between low and high, verify that timestamp has the correct timezone"""




