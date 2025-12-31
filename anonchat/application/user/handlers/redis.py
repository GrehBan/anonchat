from anonchat.infrastructure.repositories.user import mapping
from anonchat.infrastructure.cache.serialization.redis import get_data_and_decode
from anonchat.infrastructure.cache.serialization.json import load_or_none
from anonchat.infrastructure.uow.user.sqlalchemy import SqlalchemyUserUoW

class ProcessRedisUserEvent:

    async def handle(self, data: dict, uow: SqlalchemyUserUoW) -> None:
        data_type = get_data_and_decode(data, "type")

        if data_type in ("SAVE", "UPDATE"):
            raw = get_data_and_decode(data, "raw")
            user_data = load_or_none(raw)
            
            if user_data is None:
                return
            
            user = mapping.map_redis_data_to_user_entity(user_data)

            if data_type == "UPDATE":
                await uow.repo.update(user)
            else:
                if await uow.repo.get_by_id(user.id):
                    await uow.repo.update(user) 
                    return
                
                await uow.repo.add(user)

        elif data_type == "DELETE":
            _id = get_data_and_decode(data, "id")
            if _id:
                await uow.repo.delete_by_id(int(_id))
