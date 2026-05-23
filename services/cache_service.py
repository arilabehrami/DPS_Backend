import json
import os
from typing import Any, Callable

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

try:
    import redis
except ImportError:
    redis = None


def get_redis_client():
    if redis is None:
        return None

    try:
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except redis.RedisError:
        return None


def _serialize_item(item: Any, schema: type[BaseModel]) -> dict:
    return schema.model_validate(item).model_dump(mode="json")


def get_or_set_list_cache(
    key: str,
    fetch_data: Callable[[], list[Any]],
    schema: type[BaseModel],
    ttl: int = CACHE_TTL_SECONDS,
) -> list[dict]:
    client = get_redis_client()

    if client:
        cached_value = client.get(key)
        if cached_value:
            return json.loads(cached_value)

    data = fetch_data()
    serialized_data = [_serialize_item(item, schema) for item in data]

    if client:
        client.setex(key, ttl, json.dumps(serialized_data))

    return serialized_data


def invalidate_cache_prefix(prefix: str) -> None:
    client = get_redis_client()
    if not client:
        return

    for key in client.scan_iter(f"{prefix}*"):
        client.delete(key)
