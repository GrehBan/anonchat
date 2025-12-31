import logging
import os

from typing import Any

from redis.asyncio import Redis

from anonchat.domain.base.worker import IWokrker
from anonchat.domain.base.uow import UoWT


class WorkerAdapter(logging.LoggerAdapter):
    def process(self, msg: Any, kwargs: dict) -> tuple[Any, dict]:
            prefix = kwargs.get("prefix") or ""
            return f"{prefix} {msg}", kwargs


class RedisWorker(IWokrker):
    def __init__(self, redis: Redis, group_name: str | None = None, stream_key: str | None = None, shard_id: int | None = None) -> None:
        self._redis = redis
        self._running = False
        self._group_name = group_name or ""
        self._stream_key = stream_key or ""
        self._id = id(self)
        self._shard_id = shard_id or 0

        shard_prefix = f"[SHARD-{shard_id}]" if shard_id is not None else ""
        prefix = f"{shard_prefix}[PID-{os.getpid()}][ID-{self._id}]"
        
        self._logger = WorkerAdapter(
            logging.getLogger(f"{__name__}.{self.__class__.__name__}"),
            {"prefix": prefix}
        )

    @property
    def redis(self) -> Redis:
        return self._redis

    def stop(self):
        self._running = False

        self._logger.info("Stopped.")

    async def consume(self) -> None:
        raise NotImplementedError

    async def ensure_consumer_group(self, name: str):
        try:
            await self.redis.xgroup_create(
                name=name,
                groupname=self._group_name,
                id="0",
                mkstream=True
            )
            self._logger.info(f"Created consumer group '{self._group_name}'")
        except Exception as e:
            self._logger.debug(f"Consumer group exists: {e}")
