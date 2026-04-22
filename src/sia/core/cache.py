"""
Governance Caching — Performance optimization for SIA.
Stores classification and verification results to minimize redundant processing.
"""
from __future__ import annotations
import collections
from typing import Any, Dict, Optional


class GovernanceCache:
    """
    LRU In-memory cache for governance outcomes.
    Keys are typically prompt hashes or full prompts.
    """

    def __init__(self, max_size: int = 1000):
        self._data: collections.OrderedDict[str, Any] = collections.OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return None

    def set(self, key: str, value: Any):
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._max_size:
            self._data.popitem(last=False)

    def clear(self):
        self._data.clear()

    @property
    def size(self) -> int:
        return len(self._data)
