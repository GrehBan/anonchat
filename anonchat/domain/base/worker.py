from typing import Protocol


class IWokrker(Protocol):

    def stop(self) -> None:
        ...

    async def consume(self) -> None:
        ...
    
    async def process_event(self, data: dict) -> None:
        ...
    
    async def process_with_retry(self, stream: str | bytes, msg_id: str | bytes, data: dict, attempts: int = 3) -> None:
        ...

    async def move_to_dlq(self, stream: str | bytes, msg_id: str | bytes, data: dict, error: Exception) -> None:
        ...
