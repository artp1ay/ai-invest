import os
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client, SecurityTradingStatus
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal, now

from app.models import Stock, db
from peewee import DoesNotExist

from app.helpers import convert_to_csv


class TinkoffInvestmentResolver:
    class MissingApiKeyException(Exception):
        pass

    def __init__(self) -> None:
        self.tinkoff_api_key: str = os.getenv("TINKOFF_INVEST_API_KEY", "")
        self.candle_interval = CandleInterval.CANDLE_INTERVAL_HOUR
        self.database = db

        if not self.tinkoff_api_key:
            raise self.MissingApiKeyException(
                "Tinkoff API key doesn't exists. Make sure for TINKOFF_INVEST_API_KEY variable is in environment."
            )

        if not os.path.exists(os.getenv("DATABASE_FILE", "database.py")):
            db.create_tables([Stock])
            self.update_tickers_db()


    def update_tickers_db(self) -> None:
        with Client(self.tinkoff_api_key) as client:
            instruments: InstrumentsService = client.instruments
            tickers = []
            for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
                for item in getattr(instruments, method)().instruments:
                    tickers.append(
                        {
                            "name": item.name,
                            "ticker": item.ticker,
                            "class_code": item.class_code,
                            "figi": item.figi,
                            "uid": item.uid,
                            "type": method,
                            "min_price_increment": float(
                                quotation_to_decimal(item.min_price_increment)
                            ),
                            "scale": 9 - len(str(item.min_price_increment.nano)) + 1,
                            "lot": item.lot,
                            "trading_status": str(
                                SecurityTradingStatus(item.trading_status).name
                            ),
                            "api_trade_available_flag": item.api_trade_available_flag,
                            "currency": item.currency,
                            "exchange": item.exchange,
                            "buy_available_flag": item.buy_available_flag,
                            "sell_available_flag": item.sell_available_flag,
                            "short_enabled_flag": item.short_enabled_flag,
                            "klong": float(quotation_to_decimal(item.klong)),
                            "kshort": float(quotation_to_decimal(item.kshort)),
                        }
                    )

            for ticker in tickers:
                record = Stock.get_or_none(ticker=ticker["ticker"])
                if record:
                    record.name = ticker["name"]
                    record.ticker = ticker["ticker"]
                    record.save()
                else:
                    Stock.create(**ticker)

    def get_figi_by_ticker_from_db(self, ticker: str) -> str:
        stock = Stock.get_or_none(ticker=ticker)
        if stock:
            return stock.figi
        else:
            raise DoesNotExist(f"Record with ticker {ticker} not found in database.")

    def get_candles_by_ticker_name(self, ticker: str, days=5) -> list:
        output = []
        figi = self.get_figi_by_ticker_from_db(ticker)
        with Client(self.tinkoff_api_key) as client:
            for candle in client.get_all_candles(
                figi=figi,
                from_=now() - timedelta(days=days),
                interval=self.candle_interval,
            ):
                update_candle = {
                    "open": float(f"{candle.open.units}.{str(candle.open.nano)}"),
                    "close": float(f"{candle.close.units}.{str(candle.close.nano)}"),
                    "high": float(f"{candle.high.units}.{str(candle.high.nano)}"),
                    "low": float(f"{candle.low.units}.{str(candle.low.nano)}"),
                    "value": candle.volume,
                    "time": candle.time.isoformat(),
                }
                output.append(update_candle)
        return output
