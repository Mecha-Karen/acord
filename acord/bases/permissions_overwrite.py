import pydantic
from typing import Literal
from .flags.permissions import Permissions


class PermissionsOverwrite(pydantic.BaseModel):
    id: int
    type: Literal[0, 1]
    allow: Permissions
    deny: Permissions

    @pydantic.validator("type", pre=True)
    def _str_to_literal(cls, value):
        if value == "role":
            return 0
        elif value == "member":
            return 1
        return value
