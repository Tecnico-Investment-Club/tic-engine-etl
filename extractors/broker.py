'''Abstract class for the data extractors'''
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from core.models import Candle

class Broker(ABC):

    @abstractmethod
    def fetch_candles(
        self,
        asset_id: str,
        start: datetime,
        end: datetime,
        timeframe: timedelta,
    ) -> list[Candle]:
        pass


