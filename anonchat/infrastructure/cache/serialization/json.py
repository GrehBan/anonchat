from typing import Any

import logging
import orjson

logger = logging.getLogger(__name__)
loads = orjson.loads


def dumps(obj: Any) -> str:
    return orjson.dumps(obj).decode()


def load_or_none(obj: bytes | bytearray | memoryview[int] | str) -> Any | None:
    try:
        return loads(obj)
    except orjson.JSONDecodeError as e:
        logger.error("Json load error", e, exc_info=True)

    return None
