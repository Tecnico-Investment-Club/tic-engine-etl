from .broker import Broker
from core.models import Candle
from datetime import datetime, timedelta, timezone

from alpaca.data.models.bars import Bar as AlpacaBar
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class AlpacaBroker(Broker):

    def __init__(
        self,
        client: CryptoHistoricalDataClient,
        symbols: dict[str, str],
    ) -> None:
        self._client = client
        self._symbols = symbols

    def fetch_candles(
        self,
        asset_id: str,
        start: datetime,
        end: datetime,
        timeframe: timedelta,
    ) -> list[Candle]:

        if start >= end:
            raise ValueError("Start date must be before end date")
 
        if timeframe == timedelta(hours=1):
            alpaca_timeframe = TimeFrame.Hour
        elif timeframe == timedelta(days=1):
            alpaca_timeframe = TimeFrame.Day
        else:
            raise ValueError("Unsupported timeframe")

        symbol = self._symbols[asset_id]

        request = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=alpaca_timeframe,
            start=start,
            end=end,
        )

        barset = self._client.get_crypto_bars(request)

        alpaca_bars = barset.data.get(symbol, [])

        candles = []

        for bar in alpaca_bars:
            candle = self._to_candle(bar, asset_id, timeframe)
            candles.append(candle)

        return candles


    @staticmethod
    def _to_candle(
        bar: AlpacaBar,
        asset_id: str,
        timeframe: timedelta,
    ) -> Candle:
        
        for attribute in ("volume","trade_count","vwap"):
            value = getattr(bar,attribute)
            if value is not None and value < 0:
                raise ValueError(f"{attribute} must be greater than or equal to 0, can't be {value}")
        volume = -1.0 if bar.volume is None else float(bar.volume)
        trade_count = -1 if bar.trade_count is None else int(bar.trade_count)
        vwap = -1.0 if bar.vwap is None else float(bar.vwap)

        return Candle(
            open=float(bar.open),
            close=float(bar.close),
            high=float(bar.high),
            low=float(bar.low),
            asset_id=asset_id,
            broker="alpaca",
            volume=volume,
            trade_count=trade_count,
            timestamp=bar.timestamp.astimezone(timezone.utc),
            timeframe=timeframe,
            vwap=vwap,
        )