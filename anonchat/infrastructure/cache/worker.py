import logging
import asyncio
import json

from typing import Any
from datetime import datetime, timezone

from redis.asyncio import Redis

from anonchat.domain.base.worker import IWokrker

logger = logging.getLogger(__name__)


class RedisWorker(IWokrker):
    def __init__(self, redis: Redis, group_name: str | None = None, stream_key: str | None = None, shard_id: int | None = None) -> None:
        self._redis = redis
        self._running = False
        self._group_name = group_name or ""
        self._stream_key = stream_key or ""
        self._id = id(self)
        self._shard_id = shard_id or 0

    @property
    def redis(self) -> Redis:
        return self._redis

    def stop(self):
        self._running = False

        logger.info(
            f"Worker {self.__class__.__name__} "
            f"SHARD-{self._shard_id}-{self._id} Stopped."
        )

    async def consume(self) -> None:
        raise NotImplementedError
    
    async def process_event(self, data: dict):
        raise NotImplementedError

    async def ensure_consumer_group(self, name: str):
        try:
            await self.redis.xgroup_create(
                name=name,
                groupname=self._group_name,
                id="0",
                mkstream=True
            )
            logger.info(f"Created consumer group '{self._group_name}'")
        except Exception as e:
            logger.debug(f"Consumer group exists: {e}")

    async def process_with_retry(self, stream: str | bytes, msg_id: str | bytes, data: dict, attempts: int = 3) -> None:
        _, _msg_id = self._decode_stream_info(stream, msg_id)

        for attempt in range(attempts):
            try:
                await self.process_event(data)
                await self.redis.xack(stream, self._group_name, msg_id)
                return
            
            except Exception as e:
                if attempt < (attempts - 1):
                    logger.warning(f"Retry {attempt + 1}/{attempts} for {_msg_id}: {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed after {self._group_name} retries: {_msg_id}")
                    await self.move_to_dlq(stream, msg_id, data, e)
                    await self.redis.xack(stream, self._group_name, msg_id)

    async def move_to_dlq(self, stream: str | bytes, msg_id: str | bytes, data: dict, error: Exception) -> None:
        _stream, _msg_id = self._decode_stream_info(stream, msg_id)
        dlq_key = f"{_stream}:dlq"
        
        dlq_entry = {
            "original_stream": _stream,
            "original_group": self._group_name,
            "original_id": _msg_id,
            "data": json.dumps(data),
            "error": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.redis.xadd(dlq_key, dlq_entry)
        logger.error(f"Moved {_msg_id} to DLQ")

    def _decode_stream_info(self, stream: str | bytes, msg_id: str | bytes) -> tuple[str, str]:
        if isinstance(stream, bytes):
            stream = stream.decode()
        if isinstance(msg_id, bytes):
            msg_id = msg_id.decode()
        
        return stream, msg_id
    
    def _load(self, data: str) -> dict | None:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            pass

        return None

    def _get_data_and_decode(self, data: dict, key: str) -> Any:
        value = data.get(key.encode())
        if value is None:
            value = data.get(key)
        return value.decode() if isinstance(value, bytes) else value
