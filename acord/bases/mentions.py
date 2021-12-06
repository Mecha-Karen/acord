# Smaller API objects that dont need seperate files
from __future__ import annotations
from typing import List, Optional, Union

import pydantic
from acord.models import User, Message


class AllowedMentions(pydantic.BaseModel):
    roles: Optional[List[int]]
    """ List of roles to mention """
    users: Optional[List[Union[int, User]]]
    """ List of users to mention """
    replied_user: Optional[bool] = False
    """ Whether to mention to user being replied """

    # Other relevant stuff
    everyone: Optional[bool] = False
    """ Whether to allow @everyone / @here pings """
    auto: Optional[bool] = False
    """ Whether to find up a 100 roles and user mentions when they are set to False """
    deny_all: Optional[bool] = False
    """ Simply reject every single mention on message """

    parse: Optional[List[str]] = list()
    # Field should not be provided!
    # If provided just gets overwritten

    @pydantic.validator('parse')
    def _validate_parse(cls, _, **kwargs) -> list:
        kwargs = kwargs['values']

        if kwargs['deny_all']:
            return ['everyone', 'roles', 'users']

        mentions = list()

        roles = kwargs.get('roles') is not None
        users = kwargs.get('users') is not None
        everyone = kwargs.get('everyone') is not None

        if roles:
            mentions.append('roles')
        if users:
            mentions.append('users')
        if everyone:
            mentions.append('everyone')
        return mentions

    def run_auto(self, message: Message) -> None:
        if not self.auto:
            return

        user_mentions = message.mentions[:100]
        role_mentions = message.mention_roles[:100]

        self.users = list(map(lambda x: x.id, user_mentions))
        self.roles = list(map(lambda x: x.id, role_mentions))

    def dict(self, **kwargs):
        # :meta private:
        # Override pydantic to return proper AllowedMention structure
        if self.deny_all:
            return {
                "parse": ["everyone", "roles", "users"],
                "roles": [],
                "users": [],
                "replied_user": False
            }

        parsed = super(AllowedMentions, self).dict(**kwargs)
        
        parsed.pop('auto')

        parsed.pop('everyone')
        parsed.pop('deny_all')

        return parsed
