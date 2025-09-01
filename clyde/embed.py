"""Define the Embed class and its associates."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

import msgspec
from msgspec import UNSET, Meta, Struct, UnsetType


class EmbedTypes(StrEnum):
    """
    Define the available types of Discord Embeds.

    https://discord.com/developers/docs/resources/message#embed-object-embed-types

    Attributes:
        RICH (str): Generic Embed rendered from Embed attributes.
    """

    RICH = "rich"
    """Generic Embed rendered from Embed attributes."""


class EmbedFooter(Struct, kw_only=True):
    """
    Represent the Footer information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-footer-structure

    Attributes:
        text (str): Footer text.

        icon_url (UnsetType | str): URL of Footer icon (only supports HTTP(S) and Attachments).
    """

    text: Annotated[str, Meta(min_length=1, max_length=2048)] = msgspec.field()
    """Footer text."""

    icon_url: UnsetType | str = msgspec.field(default=UNSET)
    """URL of Footer icon (only supports HTTP(S) and Attachments)."""

    def set_text(self: Self, text: str) -> "EmbedFooter":
        """
        Set the text that will be displayed in the Embed Footer.

        Arguments:
            text (str): The text that will be displayed.

        Returns:
            self (EmbedFooter): The modified Embed Footer instance.
        """
        self.text = text

        return self

    def set_icon_url(self: Self, icon_url: str) -> "EmbedFooter":
        """
        Set the icon URL of the Embed Footer instance.

        Arguments:
            icon_url (str): An HTTP(S) or Attachment URL.

        Returns:
            self (EmbedFooter): The modified Embed Footer instance.
        """
        self.icon_url = icon_url

        return self


class EmbedImage(Struct, kw_only=True):
    """
    Represent the Image information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-image-structure

    Attributes:
        url (str): Source URL of image (only supports HTTP(S) and Attachments).
    """

    url: str = msgspec.field()
    """Source URL of image (only supports HTTP(S) and Attachments)."""

    def set_url(self: Self, url: str) -> "EmbedImage":
        """
        Set the URL of the Embed Image instance.

        Arguments:
            url (str): An HTTP(S) or Attachment source URL.

        Returns:
            self (EmbedImage): The modified Embed Image instance.
        """
        self.url = url

        return self


class EmbedThumbnail(Struct, kw_only=True):
    """
    Represent the Thumbnail information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-thumbnail-structure

    Attributes:
        url (str): Source URL of Thumbnail (only supports HTTP(S) and Attachments).
    """

    url: str = msgspec.field()
    """Source URL of Thumbnail (only supports HTTP(S) and Attachments)."""

    def set_url(self: Self, url: str) -> "EmbedThumbnail":
        """
        Set the URL of the Embed Thumbnail instance.

        Arguments:
            url (str): An HTTP(S) or Attachment source URL.

        Returns:
            self (EmbedThumbnail): The modified Embed Thumbnail instance.
        """
        self.url = url

        return self


class EmbedAuthor(Struct, kw_only=True):
    """
    Represent the Author information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-author-structure

    Attributes:
        name (str): Name of author.

        url (UnsetType | str): URL of author (only supports HTTP(S)).

        icon_url (UnsetType | str): URL of author icon (only supports HTTP(S) and Attachments).
    """

    name: Annotated[str, Meta(min_length=1, max_length=256)] = msgspec.field()
    """Name of author."""

    url: UnsetType | str = msgspec.field(default=UNSET)
    """URL of author (only supports HTTP(S))."""

    icon_url: UnsetType | str = msgspec.field(default=UNSET)
    """URL of author icon (only supports HTTP(S) and Attachments)."""

    def set_name(self: Self, name: str) -> "EmbedAuthor":
        """
        Set the name that will be displayed in the Embed Author.

        Arguments:
            name (str): The name that will be displayed.

        Returns:
            self (EmbedAuthor): The modified Embed Author instance.
        """
        self.name = name

        return self

    def set_url(self: Self, url: str) -> "EmbedAuthor":
        """
        Set the URL of the Embed Author instance.

        Arguments:
            url (str): An HTTP(S) URL.

        Returns:
            self (EmbedAuthor): The modified Embed Author instance.
        """
        self.url = url

        return self

    def remove_url(self: Self) -> "EmbedAuthor":
        """
        Remove the URL from the Embed Author instance.

        Returns:
            self (EmbedAuthor): The modified Embed Author instance.
        """
        self.url = UNSET

        return self

    def set_icon_url(self: Self, icon_url: str) -> "EmbedAuthor":
        """
        Set the icon URL of the Embed Author instance.

        Arguments:
            icon_url (str): An HTTP(S) or Attachment URL.

        Returns:
            self (EmbedAuthor): The modified Embed Author instance.
        """
        self.icon_url = icon_url

        return self

    def remove_icon_url(self: Self) -> "EmbedAuthor":
        """
        Remove the icon URL from the Embed Author instance.

        Returns:
            self (EmbedAuthor): The modified Embed Author instance.
        """
        self.icon_url = UNSET

        return self


class EmbedField(Struct, kw_only=True):
    """
    Represent field information in an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-field-structure

    Attributes:
        name (str): Name of the field.

        value (str): Value of the field.

        inline (UnsetType | bool): Whether or not this field should display inline.
    """

    name: Annotated[str, Meta(min_length=1, max_length=256)] = msgspec.field()
    """Name of the field."""

    value: Annotated[str, Meta(min_length=1, max_length=1024)] = msgspec.field()
    """Value of the field."""

    inline: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether or not this field should display inline."""


class Embed(Struct, kw_only=True):
    """
    Represent a Discord Embed of the Rich type.

    https://discord.com/developers/docs/resources/message#embed-object

    Attributes:
        title (UnsetType | str): Title of Embed.

        type (Final[Literal[EmbedTypes.RICH]]): The value of EmbedTypes.RICH.

        description (UnsetType | str): Description of Embed.

        url (UnsetType | str): URL of Embed.

        timestamp (UnsetType | str | int | float | datetime): Timestamp of Embed content.

        color (UnsetType | str | int): Color code of the Embed.

        footer (UnsetType | EmbedFooter): Footer information.

        image (UnsetType | EmbedImage): Image information.

        thumbnail (UnsetType | EmbedThumbnail): Thumbnail information.

        author (UnsetType | EmbedAuthor): Author information.

        fields (UnsetType | list[EmbedField]): Fields information, max of 25.
    """

    title: UnsetType | Annotated[str, Meta(min_length=1, max_length=256)] = (
        msgspec.field(default=UNSET)
    )
    """Title of Embed."""

    type: Final[Literal[EmbedTypes.RICH]] = msgspec.field(default=EmbedTypes.RICH)
    """The value of EmbedTypes.RICH."""

    description: UnsetType | Annotated[str, Meta(min_length=1, max_length=4096)] = (
        msgspec.field(default=UNSET)
    )
    """Description of Embed."""

    url: UnsetType | str = msgspec.field(default=UNSET)
    """URL of Embed."""

    timestamp: UnsetType | int | float | str | datetime = msgspec.field(default=UNSET)
    """Timestamp of Embed content."""

    color: UnsetType | str | int = msgspec.field(default=UNSET)
    """Color code of the Embed."""

    footer: UnsetType | EmbedFooter = msgspec.field(default=UNSET)
    """Footer information."""

    image: UnsetType | EmbedImage = msgspec.field(default=UNSET)
    """Image information."""

    thumbnail: UnsetType | EmbedThumbnail = msgspec.field(default=UNSET)
    """Thumbnail information."""

    author: UnsetType | EmbedAuthor = msgspec.field(default=UNSET)
    """Author information."""

    fields: (
        UnsetType | Annotated[list[EmbedField], Meta(min_length=1, max_length=25)]
    ) = msgspec.field(default=UNSET)
    """Fields information, max of 25."""

    def set_title(self: Self, title: str) -> "Embed":
        """
        Set the title of the Embed.

        Arguments:
            title (str): Title of Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.title = title

        return self

    def remove_title(self: Self) -> "Embed":
        """
        Remove the title of the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.title = UNSET

        return self

    def set_description(self: Self, description: str) -> "Embed":
        """
        Set the description of the Embed.

        Arguments:
            description (str): Description of Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.description = description

        return self

    def remove_description(self: Self) -> "Embed":
        """
        Remove the description of the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.description = UNSET

        return self

    def set_url(self: Self, url: str) -> "Embed":
        """
        Set the URL of the Embed.

        Arguments:
            url (str): URL of Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.url = url

        return self

    def remove_url(self: Self) -> "Embed":
        """
        Remove the URL of the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.url = UNSET

        return self

    def set_timestamp(self: Self, timestamp: int | float | str | datetime) -> "Embed":
        """
        Set the timestamp of the Embed.

        Arguments:
            timestamp (str | int | float | datetime): Timestamp of Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.timestamp = timestamp

        return self

    def remove_timestamp(self: Self) -> "Embed":
        """
        Remove the timestamp from the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.timestamp = UNSET

        return self

    def set_color(self: Self, color: str | int) -> "Embed":
        """
        Set the color code of the Embed.

        Arguments:
            color (str | int): Color code of the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.color = color

        return self

    def remove_color(self: Self) -> "Embed":
        """
        Remove the color of the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.color = UNSET

        return self

    def set_footer(self: Self, footer: EmbedFooter) -> "Embed":
        """
        Set the footer of the Embed.

        Arguments:
            footer (EmbedFooter): An Embed Footer.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.footer = footer

        return self

    def remove_footer(self: Self) -> "Embed":
        """
        Remove the footer from the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.footer = UNSET

        return self

    def add_image(self: Self, image: EmbedImage) -> "Embed":
        """
        Add an image to the Embed.

        Arguments:
            image (EmbedImage): An Embed Image.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.image = image

        return self

    def remove_image(self: Self) -> "Embed":
        """
        Remove an image from the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.image = UNSET

        return self

    def set_thumbnail(self: Self, thumbnail: EmbedThumbnail) -> "Embed":
        """
        Set the thumbnail of the Embed.

        Arguments:
            thumbnail (EmbedThumbnail): An Embed Thumbnail.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.thumbnail = thumbnail

        return self

    def remove_thumbnail(self: Self) -> "Embed":
        """
        Remove the thumbnail from the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.thumbnail = UNSET

        return self

    def set_author(self: Self, author: EmbedAuthor) -> "Embed":
        """
        Set the author information of the Embed.

        Arguments:
            author (EmbedAuthor): Author information.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.author = author

        return self

    def remove_author(self: Self) -> "Embed":
        """
        Remove the author information from the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.author = UNSET

        return self

    def add_field(self: Self, field: EmbedField | list[EmbedField]) -> "Embed":
        """
        Add one or more fields to the Embed.

        Arguments:
            field (EmbedField | list[EmbedField]): A field or list of fields to add to
                the Embed.

        Returns:
            self (Embed): The modified Embed instance.
        """
        if isinstance(self.fields, UnsetType):
            self.fields = []

        if isinstance(field, EmbedField):
            self.fields.append(field)
        else:
            self.fields.extend(field)

        return self

    def remove_field(self: Self, field: EmbedField | list[EmbedField] | int) -> "Embed":
        """
        Remove one or more fields from the Embed.

        Arguments:
            field (EmbedField | list[EmbedField] | int): An Embed Field, list of
                Embed Fields, or an index to remove.

        Returns:
            self (Embed): The modified Embed instance.
        """
        if isinstance(self.fields, list):
            if isinstance(field, EmbedField):
                self.fields.remove(field)
            elif isinstance(field, int):
                self.fields.pop(field)
            else:
                self.fields = [entry for entry in self.fields if entry not in field]

            # Do not retain an empty list
            if len(self.fields) == 0:
                self.fields = UNSET

        return self
