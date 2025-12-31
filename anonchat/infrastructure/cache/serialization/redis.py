from typing import Any


def get_data_and_decode(data: dict[str | bytes, bytes | Any], key: str) -> Any:
    value = data.get(key.encode())
    if value is None:
        value = data.get(key)
    return value.decode() if isinstance(value, (bytes, bytearray)) else value
