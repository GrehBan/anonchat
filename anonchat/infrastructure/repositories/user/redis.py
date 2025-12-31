import json
from typing import Final

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.user.repo import IUserRepo
from anonchat.domain.user.aggregate import User
from anonchat.infrastructure.cache import key_gen
from anonchat.infrastructure.repositories.user import mapping
from anonchat.infrastructure.cache.serialization import json

TTL: Final[int] = 86400 * 30


class RedisUserRepo(RedisRepo, IUserRepo):
    DEFAULT_TTL: int | None = TTL

    async def add(self, user: User) -> User:
        await self._save(user)

        return user

    async def update(self, user: User) -> User:
        await self._save(user, event_type="UPDATE")

        return user

    async def _save(self, user: User, event_type: str = "SAVE") -> None:
        data = mapping.map_user_entity_to_redis_data(user)
        
        raw = json.dumps(data)
        key = key_gen.user_data(user.id)

        async with self.redis.pipeline() as pipe:
            pipe.set(key, raw, ex=self._ttl)
            
            pipe.xadd(key_gen.get_user_stream(user.id), {"type": event_type, "raw": raw})
            
            await pipe.execute()

    async def get_by_id(self, id: int) -> User | None:
        raw = await self.redis.get(key_gen.user_data(id))
        if not raw:
            return None
        
        data = json.loads(raw)
        
        return mapping.map_redis_data_to_user_entity(data)


    async def delete_by_id(self, id: int) -> None:
        async with self.redis.pipeline() as pipe:
            pipe.delete(key_gen.user_data(id))
            pipe.xadd(key_gen.get_user_stream(id), {"type": "DELETE", "id": str(id)})
            await pipe.execute()
