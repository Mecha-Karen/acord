from __future__ import annotations
from typing import Any, List, Literal, Optional

import pydantic
from pydantic.color import Color
import datetime


class EmbedFooter(pydantic.BaseModel):
    text: str
    icon_url: Optional[pydantic.AnyHttpUrl]
    proxy_icon_url: Optional[pydantic.AnyHttpUrl]


class EmbedAuthor(pydantic.BaseModel):
    name: str
    url: Optional[pydantic.AnyHttpUrl]
    icon_url: Optional[pydantic.AnyHttpUrl]
    proxy_icon_url: Optional[pydantic.AnyHttpUrl]


class EmbedField(pydantic.BaseModel):
    name: str
    value: str
    inline: Optional[bool] = True


class EmbedImage(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    proxy_url: Optional[pydantic.AnyHttpUrl]
    height: Optional[int]
    width: Optional[int]

class EmbedThumbnail(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    proxy_url: Optional[pydantic.AnyHttpUrl]
    height: Optional[int]
    width: Optional[int]


class EmbedVideo(pydantic.BaseModel):
    url: Optional[str]
    proxy_url: Optional[pydantic.AnyHttpUrl]
    height: Optional[int]
    width: Optional[int]


class EmbedProvidor(pydantic.BaseModel):
    name: Optional[str]
    url: Optional[pydantic.AnyHttpUrl]

class Embed(pydantic.BaseModel):
    title: Optional[str]
    """ Embed title """
    type: Optional[Literal["rich", "image", "video", "gifv", "article", "link"]] = "rich"
    """ Embed type, defaults to rich """
    description: Optional[str]
    """ Embed description """
    url: Optional[pydantic.AnyHttpUrl]
    """ Embed title hyperlink """
    timestamp: Optional[datetime.datetime]
    """ Embed timestamp """
    color: Optional[Color]
    """ Embed colour """
    footer: Optional[EmbedFooter]
    """ Embed footer """
    image: Optional[EmbedImage]
    """ Embed image """
    thumbnail: Optional[EmbedThumbnail]
    """ Embed thumbnail """
    video: Optional[EmbedVideo]
    """ Embed video """
    providor: Optional[EmbedProvidor]
    """ Embed Providor """
    author: Optional[EmbedAuthor]
    """ Embed author """
    fields: Optional[List[EmbedField]]
    """ Embed fields """

    @pydantic.validator('title')
    def _validate_title(cls, title: str) -> str:
        if len(title) > 256:
            raise ValueError('Title cannot be greater then 256 characters')
        return title

    @pydantic.validator('description')
    def _validate_desc(cls, desc: str) -> str:
        if len(desc) > 4096:
            raise ValueError('Description cannot be greater then 4096 characters')
        return desc

    def set_footer(self, **data) -> None:
        """
        Add footer on embed

        Parameters
        ----------
        text: :class:`str`
            Footer text
        icon_url: :class:`str`
            Footer icon url
        proxy_icon_url: :class:`str`
            A proxied url of footer icon
        """
        footer = EmbedFooter(**data)
        self.footer = footer

    def set_author(self, **data) -> None:
        """
        Add author on embed

        Parameters
        ----------
        name: :class:`str`
        url: :class:`str`
        icon_url: :class:`str`
        proxy_icon_url: :class:`str`
        """
        author = EmbedAuthor(**data)
        self.author = author
