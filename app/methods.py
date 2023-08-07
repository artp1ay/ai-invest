from app.ai import AITemplateResolver
from app.tksinvest import TinkoffInvestmentResolver
from app.helpers import *
from app.models import Stock, db
import requests


def get_or_set_by_ticker(ticker: str, template: str, days=5) -> dict:
    ticker_key = f"{ticker}-{str(days)}"
    prediction = AITemplateResolver()

    if not r.exists(ticker_key):
        data = TinkoffInvestmentResolver().get_candles_by_ticker_name(ticker)
        data = convert_to_csv(data)
        prediction = prediction.openai_get_response(
            ticker=ticker, template=template, days=days, csv_data=data
        )
        add = check_redis_key_and_add(
            ticker_key, encode_payload(prediction), os.getenv("PREDICTION_TTL", "")
        )
        return prediction
    else:
        result = r.get(ticker_key)
        result = decode_payload(result)
        return result


def update_tickers() -> None:
    data = TinkoffInvestmentResolver().update_tickers_db()
    return

def get_trends():
    data = requests.get("https://www.tinkoff.ru/api/invest/catalog/shelves/list?id=23f98f95-4705-4890-b182-6b8c07e0638e&sessionId=7IcAq9nWQUg8qsT5MCVtnRNVHdKcNjuA.m1-prod-api63&appName=web&appVersion=1.350.0&origin=web")
    if data.json()['payload']['data']:
        return data.json()['payload']['data']
    else:
        return {}
