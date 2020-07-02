import logging
import time
from typing import Optional, Callable

from pickledb import PickleDB

logger = logging.getLogger(__name__)


class FetchError(Exception):
    pass


class CacheEntry:
    def __init__(self, update_time, success, data):
        self.update_time = update_time
        self.success = success
        self.data = data


class CachedData:
    data = None

    def __init__(self, fetch: Callable, db: PickleDB, key: str, refresh_interval: int = 60):
        self.fetch = fetch
        self.db = db
        self.key = key
        self.refresh_interval = refresh_interval
        self.refresh()

    def refresh(self):
        now = time.time()

        if not self.data:
            cached_data = self.db.get(self.key)
            if cached_data:
                self.data = cached_data

        if not self.data or now - self.data['update_time'] > self.refresh_interval:
            try:
                logger.error(f"Fetching {self.key}...")
                self.data = {
                    'update_time': now,
                    'success': True,
                    'data': self.fetch(),
                }
            except:
                self.data = {
                    'update_time': now,
                    'success': False
                }
                logger.error("Failed to fetch data", exc_info=True)
            self.db.set(self.key, self.data)
            self.db.dump()

    def get(self):
        self.refresh()
        data = self.data
        if data['success']:
            return data['data']
        else:
            raise FetchError()
