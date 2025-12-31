import asyncio
from datetime import datetime, timezone

from redis.asyncio import Redis

from anonchat.infrastructure.cache.worker import RedisWorker
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.message.redis import RedisMessageRepo
from anonchat.infrastructure.cache.serialization import json


class CompactMessagesWorker(RedisWorker):
    def __init__(
        self, 
        redis: Redis, 
        scan_interval: int = 300,
        min_deleted_ratio: float = 0.1,
        batch_size: int = 100
    ):
        super().__init__(redis)
        self._scan_interval = scan_interval
        self._min_deleted_ratio = min_deleted_ratio
        self._batch_size = batch_size
        self._repo = RedisMessageRepo(redis)
        
        self._total_compacted = 0
        self._last_run: datetime | None = None

    async def process_event(self, chat_id: int) -> int:
        try:
            deleted_count = await self._repo.compact_timeline(chat_id)
            
            if deleted_count > 0:
                self._logger.info(
                    f"Compacted chat {chat_id}: removed {deleted_count} deleted messages"
                )
                self._total_compacted += deleted_count
            
            return deleted_count
            
        except Exception as e:
            self._logger.error(f"Error compacting chat {chat_id}: {e}", exc_info=True)
            return 0

    async def should_compact(self, chat_id: int) -> bool:
        timeline_key = key_gen.chat_messages_timeline(chat_id)
        
        msg_ids = await self.redis.lrange(timeline_key, 0, -1)
        msg_keys = [key_gen.message_data(int(mid)) for mid in msg_ids]
        
        deleted_count = 0
        async with self.redis.pipeline() as pipe:
            for key in msg_keys:
                pipe.get(key)
            
            results = await pipe.execute()
            
            for raw in results:
                if raw:
                    data = json.loads(raw)
                    if data.get("del_at"):
                        deleted_count += 1
        
        deleted_ratio = deleted_count / len(msg_ids)
        
        self._logger.debug(
            f"Chat {chat_id}: {deleted_count}/{len(msg_ids)} deleted "
            f"({deleted_ratio:.1%})"
        )
        
        return deleted_ratio >= self._min_deleted_ratio

    async def consume(self) -> None:
        self._running = True
        self._logger.info(
            f"Started "
            f"(interval: {self._scan_interval}s, "
            f"min_ratio: {self._min_deleted_ratio:.0%})"
        )

        while self._running:
            try:
                scan_start = datetime.now(timezone.utc)
                
                cursor = 0
                pattern = key_gen.CHAT_MESSAGES_PATTERN
                chats_scanned = 0
                chats_compacted = 0
                
                while self._running:
                    cursor, keys = await self.redis.scan(
                        cursor=cursor,
                        match=pattern,
                        count=self._batch_size
                    )
                    
                    for key in keys:
                        try:
                            chat_id = key_gen.extract_chat_id_from_timeline_key(key)
                        except (IndexError, ValueError):
                            self._logger.warning(f"Invalid timeline key format: {key}")
                            continue
                        
                        chats_scanned += 1
                        
                        if await self.should_compact(chat_id):
                            deleted = await self.process_event(chat_id)
                            if deleted > 0:
                                chats_compacted += 1
                        
                        await asyncio.sleep(0.01)
                    
                    if cursor == 0:
                        break
                    
                    await asyncio.sleep(0.1)
                
                scan_duration = (datetime.now(timezone.utc) - scan_start).total_seconds()
                self._last_run = scan_start
                
                self._logger.info(
                    f"Compaction cycle completed: "
                    f"scanned={chats_scanned}, compacted={chats_compacted}, "
                    f"duration={scan_duration:.1f}s, total_deleted={self._total_compacted}"
                )
                
                await asyncio.sleep(self._scan_interval)
            
            except Exception as e:
                self._logger.error(f"Compaction worker error: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    def get_metrics(self) -> dict:
        return {
            "total_compacted": self._total_compacted,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "running": self._running
        }

