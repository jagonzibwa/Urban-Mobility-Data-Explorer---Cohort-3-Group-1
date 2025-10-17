from collections import OrderedDict
from typing import Generic, TypeVar, Optional

K = TypeVar('K')
V = TypeVar('V')


class LRUCache(Generic[K, V]):
    """Simple LRU (Least Recently Used) cache with O(1) get/put.

    Uses OrderedDict to keep recent items at the end. When capacity is
    exceeded, the least-recently used item is evicted.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity: int = capacity
        self._store: "OrderedDict[K, V]" = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        if key not in self._store:
            return None
        # Move to end to mark as recently used
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: K, value: V) -> None:
        if key in self._store:
            # Update and mark as recently used
            self._store.move_to_end(key)
            self._store[key] = value
        else:
            self._store[key] = value
            # Evict least recently used
            if len(self._store) > self._capacity:
                self._store.popitem(last=False)

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: K) -> bool:
        return key in self._store


