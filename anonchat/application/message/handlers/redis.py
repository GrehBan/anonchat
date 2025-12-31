from anonchat.infrastructure.repositories.message import mapping
from anonchat.infrastructure.cache.serialization.redis import get_data_and_decode
from anonchat.infrastructure.cache.serialization.json import load_or_none
from anonchat.infrastructure.uow.message.sqlalchemy import SqlalchemyMessageUoW

class ProcessRedisMessageEvent:

    async def handle(self, data: dict, uow: SqlalchemyMessageUoW) -> None:
        data_type = get_data_and_decode(data, "type")

        if data_type == "SAVE":
            raw = get_data_and_decode(data, "raw")
            message_data = load_or_none(raw)
            
            if message_data is None:
                return
            
            message = mapping.map_redis_data_to_message_entity(message_data)
            
            if await uow.repo.get_by_id(message.id):
                return
            
            await uow.repo.add(message)

        elif data_type == "SOFT_DELETE":
            _id = get_data_and_decode(data, "id")
            if _id:
                await uow.repo.delete(int(_id))
