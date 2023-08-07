import os
import csv
from io import StringIO
import redis
import pickle

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
)


def convert_to_csv(data: list) -> str:
    csv_string = StringIO()
    csv_writer = csv.writer(csv_string)
    csv_writer.writerow(data[0].keys())
    for item in data:
        csv_writer.writerow(item.values())

    csv_string = csv_string.getvalue()
    return csv_string


def check_redis_key_and_add(key: str, value: str, expire: int) -> None:
    if not r.exists(key):
        r.setex(key, expire, value)


def encode_payload(payload: dict):
    return pickle.dumps(payload)


def decode_payload(payload: bytes) -> dict:
    return pickle.loads(payload)
