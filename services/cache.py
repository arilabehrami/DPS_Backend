import json
import os
import time
from typing import Any

try:
    import redis
except ImportError:  # pragma: no cover - dependency is optional at runtime
    redis = None


class CacheService:
    def __init__(self):
        self._memory: dict[str, tuple[float, str]] = {}
        self._redis = None

        redis_url = os.getenv("REDIS_URL")
        if redis and redis_url:
            try:
                self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    @property
    def backend(self) -> str:
        return "redis" if self._redis else "memory"

    def get(self, key: str) -> Any | None:
        if self._redis:
            raw = self._redis.get(key)
            return json.loads(raw) if raw else None

        item = self._memory.get(key)
        if not item:
            return None

        expires_at, raw = item
        if expires_at < time.time():
            self._memory.pop(key, None)
            return None
        return json.loads(raw)

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        raw = json.dumps(value)
        if self._redis:
            self._redis.setex(key, ttl_seconds, raw)
            return

        self._memory[key] = (time.time() + ttl_seconds, raw)

    def delete(self, key: str) -> None:
        if self._redis:
            self._redis.delete(key)
            return
        self._memory.pop(key, None)


cache_service = CacheService()
