import time

import pytest

from services.cache import CacheService


@pytest.mark.no_db
def test_memory_cache_set_get_delete(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    cache = CacheService()

    assert cache.backend == "memory"
    cache.set("k1", {"ok": True}, ttl_seconds=10)
    assert cache.get("k1") == {"ok": True}

    cache.delete("k1")
    assert cache.get("k1") is None


@pytest.mark.no_db
def test_memory_cache_ttl_expiry(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    cache = CacheService()

    cache.set("k2", {"n": 1}, ttl_seconds=1)
    assert cache.get("k2") == {"n": 1}

    time.sleep(1.1)
    assert cache.get("k2") is None

