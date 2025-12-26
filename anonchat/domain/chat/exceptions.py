from anonchat.domain.base.exceptions import DomainException


class ChatNotFoundException(DomainException):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat {chat_id} not found")


class ChatClosedException(DomainException):
    pass
