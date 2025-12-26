from typing import TypeVar

from pydantic import BaseModel, ConfigDict

DTOT = TypeVar("DTOT", bound="BaseDTO")


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        from_attributes=True
    )
