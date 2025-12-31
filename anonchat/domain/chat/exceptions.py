from anonchat.domain.base.exceptions import NotFoundException, PermissionDeniedException


class ChatNotFoundException(NotFoundException):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat {chat_id} not found")


class ChatClosedException(PermissionDeniedException):
    pass
