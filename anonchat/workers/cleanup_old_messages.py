import asyncio
import logging

from anonchat.infrastructure.cache.worker import RedisWorker

logger = logging.getLogger(__name__)


class CleanupMessagesWorker(RedisWorker):

    async def process_event(self, key: str):
        length = await self.redis.llen(key)
        if length > 1000:
            await self.redis.ltrim(key, -1000, -1)

    async def consume(self) -> None:
        self._running = True
        logger.info(f"{self.__class__.__name__} Started")

        while self._running:
            try:
                cursor = 0
                pattern = "chat:*:timeline"
                
                while self._running:
                    cursor, keys = await self.redis.scan(
                        cursor=cursor,
                        match=pattern,
                        count=100
                    )
                    
                    for key in keys:
                        await self.process_event(key)
                    
                    if cursor == 0:
                        break
                
                await asyncio.sleep(60)
            
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}", exc_info=True)
                await asyncio.sleep(5)
