# Smaller API objects that dont need seperate files
from __future__ import annotations
from typing import List, Optional

import pydantic


class AllowedMentions(pydantic.BaseModel):
    roles: Optional[List[int]]
    """ List of roles to mention """
    users: Optional[List[int]]
    """ List of users to mention """
    replied_user: Optional[bool] = False
    """ Whether to mention to user being replied """

    # Other relevant stuff
    everyone: Optional[bool] = False
    """ Whether to allow @everyone / @here pings """
    deny_all: Optional[bool] = False
    """ Simply reject every single mention on message """

    parse: Optional[List[str]] = list()
    # Field should not be provided!
    # If provided just gets overwritten

    @pydantic.validator("parse")
    def _validate_parse(cls, _, **kwargs) -> list:
        kwargs = kwargs["values"]

        if kwargs["deny_all"]:
            return ["everyone", "roles", "users"]

        mentions = list()

        roles = kwargs.get("roles") is not None
        users = kwargs.get("users") is not None
        everyone = kwargs.get("everyone") is not None

        if roles:
            mentions.append("roles")
        if users:
            mentions.append("users")
        if everyone:
            mentions.append("everyone")
        return mentions

    def dict(self, **kwargs):
        """ :meta private: """
        # Override pydantic to return proper AllowedMention structure
        if self.deny_all:
            return {"parse": []}

        parsed = super(AllowedMentions, self).dict(**kwargs)

        parsed.pop("everyone")
        parsed.pop("deny_all")

        return parsed
