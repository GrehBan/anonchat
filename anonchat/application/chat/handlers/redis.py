from anonchat.infrastructure.repositories.chat import mapping
from anonchat.infrastructure.cache.serialization.redis import get_data_and_decode
from anonchat.infrastructure.cache.serialization.json import load_or_none

from anonchat.domain.chat.handlers.redis import IChatDbEventHandler
from anonchat.infrastructure.uow.chat.sqlalchemy import SqlalchemyChatUoW


class ProcessRedisChatEvent(IChatDbEventHandler[SqlalchemyChatUoW]):

    async def handle(self, data: dict, uow: SqlalchemyChatUoW):

        data_type = get_data_and_decode(data, "type")

        if data_type == "CREATE":

            raw = get_data_and_decode(data, "raw")
            chat_data = load_or_none(raw)

            if chat_data is None:
                return
            
            chat = mapping.map_redis_data_to_chat_entity(chat_data)
            if (await uow.repo.get_by_id(chat.id)):
                return
            await uow.repo.add(chat)

        elif data_type == "CLOSE":

            _id = get_data_and_decode(data, "id")
            chat = await uow.repo.get_by_id(chat_id=int(_id))
            
            if chat is not None:
                chat.is_active = False
                await uow.repo.update(chat)
