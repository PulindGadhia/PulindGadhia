"""Filesystem caching implementation."""

import pickle
import time
from pathlib import Path
from typing import Any, Optional

from github_profiler.domain.interfaces import ICache


class LocalFSCache(ICache):
    """Local filesystem cache for GitHub API data and processed assets."""

    def __init__(self, cache_dir: Path) -> None:
        """Initializes the cache directory.

        Args:
            cache_dir: The path to store cache files.
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        cache_file = self.cache_dir / f"{key}.pkl"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                data = pickle.load(f)

            if "expiry" in data and time.time() > data["expiry"]:
                cache_file.unlink()
                return None

            return data.get("value")
        except (pickle.PickleError, OSError):
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            data = {
                "expiry": time.time() + ttl_seconds,
                "value": value
            }
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
        except OSError:
            pass
