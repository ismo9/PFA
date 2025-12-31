from time import time
from typing import Any, Dict, Tuple

class TTLCache:
    def __init__(self):
        self._store: Dict[str, Tuple[float, Any]] = {}

    def _now(self) -> float:
        return time()

    def get(self, key: str) -> Any:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if self._now() > expires_at:
            # expired
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        self._store[key] = (self._now() + max(1, ttl_seconds), value)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

# Singleton cache for app-wide use
cache = TTLCache()
