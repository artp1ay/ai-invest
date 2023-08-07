from peewee import *
import json
import os


db = SqliteDatabase(os.getenv("DATABASE_FILE", "database.db"))


class BaseModel(Model):
    class Meta:
        database = db


class Stock(BaseModel):
    name = CharField()
    ticker = CharField()
    class_code = CharField()
    figi = CharField()
    uid = CharField()
    type = CharField()
    min_price_increment = FloatField()
    scale = IntegerField()
    lot = IntegerField()
    trading_status = CharField()
    api_trade_available_flag = CharField()
    currency = CharField()
    exchange = CharField()
    buy_available_flag = CharField()
    sell_available_flag = CharField()
    short_enabled_flag = CharField()
    klong = FloatField()
    kshort = FloatField()
