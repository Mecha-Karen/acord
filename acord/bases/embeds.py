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

    @pydantic.validator('color')
    def _validate_colour(cls, desc):
        return desc.as_hex()

    def characters(self) -> int:
        """ Counts the total amount of characters in the embed """
        count = 0

        count += len((self.title or ""))
        count += len((self.description or ""))
        
        footer_text = getattr(self.footer, 'text', "")
        count += len(footer_text)

        author_text = getattr(self.author, 'name', "")
        count += len(author_text)

        for field in (self.fields or list()):
            count += len((field.name or ""))
            count += len((field.value or ""))

        return count

    def set_footer(self, **data) -> None:
        """
        Add footer on embed

        Parameters
        ----------
        text: :class:`str`
            Footer text
        icon_url: :class:`str`
            A url for the icon url
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
            Author name
        url: :class:`str`
            URL of author
        icon_url: :class:`str`
            A url for the author icon
        proxy_icon_url: :class:`str`
            A proxied url of author icon
        """
        author = EmbedAuthor(**data)
        self.author = author

    def add_field(self, **data) -> None:
        """
        Add a new field to your embed

        Parameters
        ----------
        name: :class:`str`
            Name of field
        value: :class:`str`
            Value of field
        inline: :class:`bool`
            Whether or not this field should be inline. Defaults to ``False``
        """
        field = EmbedField(**data)

        fields = self.fields

        if (len(fields) + 1) > 21:
            raise ValueError('Embed cannot contain more then 21 fields')
        
        fields.append(field)
        self.fields = field

    def remove_field(self, index: int) -> Optional[EmbedField]:
        """
        Remove a field from the embed,
        Returns field if found,
        Else raises :class:`IndexError`.

        Parameters
        ----------
        index: :class:`int`
            Index of field to remove.
        """
        fields = self.fields

        x = fields.pop(index)
        self.fields = fields
        return x

    def insert_field(self, index, **data) -> None:
        """
        Insert a field at a certain index

        Parameters
        ----------
        index: :class:`int`
            Index to insert field at, e.g. ``0`` is the start
        """
        fields = self.fields
        field = EmbedField(**data)

        fields.insert(index, field)
        self.fields = fields
