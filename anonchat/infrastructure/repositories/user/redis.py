import json
from redis.asyncio import Redis

from anonchat.infrastructure.repositories.base.redis import RedisRepo
from anonchat.domain.user.repo import IUserRepo
from anonchat.domain.user.aggregate import User
from anonchat.domain.user.value_object import UserSettings, Reputation, Status, Interests
from anonchat.infrastructure.cache import key_gen


class RedisUserRepo(RedisRepo, IUserRepo):

    async def add(self, user: User) -> User:
        await self._save(user)

        return user

    async def _save(self, user: User) -> None:
        data = {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "locale": user.locale,
            "gender": user.gender,
            "settings": {
                "search_gender": user.settings.search_gender,
                "min_age": user.settings.min_age,
                "max_age": user.settings.max_age
            },
            "reputation": {
                "likes": user.reputation.likes,
                "dislikes": user.reputation.dislikes
            },
            "status": {
                "val": user.status.user_status,
                "promo": user.status.promotion,
                "vip": user.status.vip
            },
            "interests": list(user.interests.user_interests)
        }
        
        raw = json.dumps(data)
        key = key_gen.user_data(user.id)

        async with self.redis.pipeline() as pipe:
            pipe.set(key, raw)
            
            pipe.xadd(key_gen.STREAM_USERS, {"type": "SAVE", "data": raw})
            
            await pipe.execute()

    async def get_by_id(self, id: int) -> User | None:
        raw = await self.redis.get(key_gen.user_data(id))
        if not raw:
            return None
        
        data = json.loads(raw)
        
        return User(
            id=data["id"],
            full_name=data["full_name"],
            username=data["username"],
            locale=data["locale"],
            gender=data["gender"],
            settings=UserSettings(
                search_gender=data["settings"]["search_gender"],
                min_age=data["settings"]["min_age"],
                max_age=data["settings"]["max_age"]
            ),
            reputation=Reputation(
                likes=data["reputation"]["likes"],
                dislikes=data["reputation"]["dislikes"]
            ),
            status=Status(
                user_status=data["status"]["val"],
                promotion=data["status"]["promo"],
                vip=data["status"]["vip"]
            ),
            interests=Interests(set(data["interests"]))
        )

    async def delete_by_id(self, id: int) -> None:
        async with self.redis.pipeline() as pipe:
            pipe.delete(key_gen.user_data(id))
            pipe.xadd(key_gen.STREAM_USERS, {"type": "DELETE", "id": str(id)})
            await pipe.execute()
