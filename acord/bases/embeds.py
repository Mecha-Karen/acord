from __future__ import annotations
from typing import Any, List, Literal, Optional

import pydantic
from pydantic.color import Color as PydanticColor
import datetime


def _rgb_to_hex(rgb) -> str:
    string = ""
    for i in rgb:
        val = hex(i)[2:]
        if len(val) == 1:
            string += '0' + val
        else:
            string += val
    return string

class Color(PydanticColor):
    def __init__(self, color) -> None:
        if isinstance(color, int):
            # Converts int into a 6 char hex code
            color = f'#{color:0>6X}'
        
        super().__init__(color)

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
    url: Optional[pydantic.AnyHttpUrl]
    proxy_url: Optional[pydantic.AnyHttpUrl]
    height: Optional[int]
    width: Optional[int]


class EmbedProvidor(pydantic.BaseModel):
    name: Optional[str]
    url: Optional[pydantic.AnyHttpUrl]

class Embed(pydantic.BaseModel):
    """ An object representing a discord embed """

    title: Optional[str] = None
    """ Embed title, must be under 256 chars if provided """
    type: Literal["rich", "image", "video", "gifv", "article", "link"] = "rich"
    """ Embed type, defaults to rich """
    description: Optional[str] = None
    """ Embed description, must be under 4096 chars if provided """
    url: Optional[pydantic.AnyHttpUrl] = None
    """ Embed title hyperlink """
    timestamp: Optional[datetime.datetime] = None
    """ Embed timestamp """
    color: Optional[Color] = None
    """Embed colour,
    can be any value as per `CSS3 specifications <http://www.w3.org/TR/css3-color/#svg-color>`_

    .. rubric:: Allowed Forms

    .. code-block:: py

        Embed(color="hsl(260, 50%, 20%)")
        Embed(color="rgb(10, 10, 10)")
        Embed(color="rgba(10, 10, 10, 0.1)")
        Embed(color="#LongHex")
        Embed(color="#ShortHex")
        Embed(color="Hex or ShortHex")
        Embed(color=Hex)
        Embed(color="blue")
    """
    footer: Optional[EmbedFooter] = None
    """ Embed footer """
    image: Optional[EmbedImage] = None
    """ Embed image """
    thumbnail: Optional[EmbedThumbnail] = None
    """ Embed thumbnail """
    video: Optional[EmbedVideo] = None
    """ Embed video """
    providor: Optional[EmbedProvidor] = None
    """ Embed Providor """
    author: Optional[EmbedAuthor] = None
    """ Embed author """
    fields: List[EmbedField] = pydantic.Field(default_factory=list)
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

    def characters(self) -> int:
        """ Counts the total amount of characters in the embed """
        count = 0

        if self.title is not None:
            count += len(self.title)

        if self.description is not None:
            count += len(self.description)
        
        if self.footer is not None:
            count += len(self.footer.text)

        if self.author is not None:
            count += len(self.author.name)

        for field in self.fields:
            count += len(field.name)
            count += len(field.value)

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

        if len(self.fields) + 1 > 21:
            raise ValueError('Embed cannot contain more then 21 fields')

        field = EmbedField(**data)

        self.fields.append(field)

    def remove_field(self, index: int) -> EmbedField:
        """
        Remove a field from the embed,
        Returns field if found,
        Else raises :class:`IndexError`.

        Parameters
        ----------
        index: :class:`int`
            Index of field to remove.
        """

        popped_field = self.fields.pop(index)
        return popped_field

    def insert_field(self, index, **data) -> None:
        """
        Insert a field at a certain index

        Parameters
        ----------
        index: :class:`int`
            Index to insert field at, e.g. ``0`` is the start
        """

        field = EmbedField(**data)
        self.fields.insert(index, field)

    def dict(self, *args, **kwargs) -> dict:
        # :meta private:
        # Override pydantic to return `Color` as a hex
        data = super(Embed, self).dict(*args, **kwargs)

        if self.color is not None:
            color = int(_rgb_to_hex(self.color.as_rgb_tuple(alpha=False)), 16)
            data['color'] = color

        return data
