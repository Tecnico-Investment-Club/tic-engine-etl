from dataclasses import dataclass,fields
from datetime import datetime,timedelta,timezone
from math import isfinite

#used in _checked types , if we add new attribute to candle must add it to the dict to ensure proper typechecking
TYPES = {
    float: ("open","close","high","low","volume","vwap"),
    int: ("trade_count",),
    str: ("asset_id","broker"),
    datetime: ("timestamp",),
    timedelta: ("timeframe",)
}

#use in _check_price
PRICE_ATTRIBUTES = ("open","close","low","high")  

@dataclass(frozen=True,slots=True,kw_only=True)
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

    
    def __post_init__(self) -> None:
        self._check_types()
        self._check_prices()
        self._check_volume()
        self._check_time()


    def _check_types(self) -> None:
        for expected, attributes in TYPES.items():
            for attribute in attributes:
                value = getattr(self,attribute)
                if isinstance(value,bool) or not isinstance(value,expected):  ### Because bool is subclass of int check that trade_coutn !=True
                    raise TypeError(f"{attribute} must be a {expected.__name__} not a {type(value).__name__}")            
                if expected in (int,float) and not isfinite(value):
                    raise ValueError(f"{attribute} must be a finite number not infinity")
                if expected == str and not value.strip():
                    raise ValueError(f"{attribute} can not be an empty string, it must have a value")   

    def _check_prices(self) -> None:
        for attribute in PRICE_ATTRIBUTES:
            value = getattr(self,attribute)
            if value <= 0:
                raise ValueError(f"{attribute} must be a positive value not: {value}")
        
        if self.high < max(self.open,self.close,self.low):
            raise  ValueError("Inconsistency in pricing, high must be bigger than open,close and low")

        if self.low > min(self.open,self.close,self.high):
            raise ValueError("Inconsistency in pricing, low must be smaller than opne,close and high")

        if self.trade_count >0 and self.vwap != -1 and not (self.low <= self.vwap <= self.high): ##only check vwap if there were trades, if there were no trades then vwap=0 and low= open which will fail the test dispite logical input. avearage only makes sense if there were trades
            raise ValueError("vwap must be between low and high, since it's an average")


    def _check_volume(self) -> None:
        for attribute in ("volume","trade_count","vwap"):
            value = getattr(self,attribute)
            if value < 0 and value != -1:
                raise ValueError(f"{attribute} must be greater than or equal to 0, can't be {value}")
        if self.volume != -1 and self.trade_count != -1:
            if (self.volume == 0) != (self.trade_count == 0):
                raise ValueError("if either trade count or volume is 0, then they must both be 0")
        
    def _check_time(self) -> None: 
        if self.timestamp.tzinfo != timezone.utc:
            raise ValueError(f"timestamp must be in UTC, got {self.timestamp.tzinfo}")

        if self.timeframe <= timedelta(0):
            raise ValueError(f"timeframe must be a positive amount of time can not be {self.timeframe}")



#if we add a new attribute to candle this checks that the new value is also passing through the _check_types 
# and not just being ignored becuase its not in the TYPES dict
checked_attributes = []
for attributes in TYPES.values():
    for attribute in attributes:
        checked_attributes.append(attribute)

candle_attributes = []
for attribute in fields(Candle):
    candle_attributes.append(attribute.name)

if sorted(checked_attributes) != sorted(candle_attributes):
    raise RuntimeError("Not all candle attributes are being type checked")
    
