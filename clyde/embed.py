"""Define the Embed class and its associates."""

from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from clyde.validation import Validation


class EmbedTypes(StrEnum):
    """
    Define the available types of Discord Embeds.

    https://discord.com/developers/docs/resources/message#embed-object-embed-types

    Attributes:
        RICH (str): Generic Embed rendered from Embed attributes.
    """

    RICH = "rich"
    """Generic Embed rendered from Embed attributes."""


class EmbedFooter(BaseModel):
    """
    Represent the Footer information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-footer-structure

    Attributes:
        text (str): Footer text.

        icon_url (str | None): URL of Footer icon (only supports HTTP(S) and Attachments).
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed Footer class."""

    text: str | None = Field(default=None, max_length=2048)
    """Footer text."""

    icon_url: str | None = Field(default=None)
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

    @field_validator("icon_url", mode="after")
    @classmethod
    def _validate_icon_url(cls, icon_url: str) -> str:
        """
        Validate the value of icon URL for an Embed Footer.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(icon_url, ["http", "https", "attachment"])


class EmbedImage(BaseModel):
    """
    Represent the Image information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-image-structure

    Attributes:
        url (str): Source URL of image (only supports HTTP(S) and Attachments).
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed Image class."""

    url: str | None = Field(default=None)
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

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """
        Validate the value of URL for an Embed Image.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(url, ["http", "https", "attachment"])


class EmbedThumbnail(BaseModel):
    """
    Represent the Thumbnail information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-thumbnail-structure

    Attributes:
        url (str): Source URL of Thumbnail (only supports HTTP(S) and Attachments).
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed Thumbnail class."""

    url: str | None = Field(default=None)
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

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """
        Validate the value of URL for an Embed Thumbnail.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(url, ["http", "https", "attachment"])


class EmbedAuthor(BaseModel):
    """
    Represent the Author information of an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-author-structure

    Attributes:
        name (str): Name of author.

        url (str | None): URL of author (only supports HTTP(S)).

        icon_url (str | None): URL of author icon (only supports HTTP(S) and Attachments).
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed Author class."""

    name: str | None = Field(default=None, max_length=256)
    """Name of author."""

    url: str | None = Field(default=None)
    """URL of author (only supports HTTP(S))."""

    icon_url: str | None = Field(default=None)
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

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """
        Validate the value of URL for an Embed Author.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(url, ["http", "https"])

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

    @field_validator("icon_url", mode="after")
    @classmethod
    def _validate_icon_url(cls, icon_url: str) -> str:
        """
        Validate the value of icon URL for an Embed Author.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(icon_url, ["http", "https", "attachment"])


class EmbedField(BaseModel):
    """
    Represent field information in an Embed.

    https://discord.com/developers/docs/resources/message#embed-object-embed-field-structure

    Attributes:
        name (str): Name of the field.

        value (str): Value of the field.

        inline (bool | None): Whether or not this field should display inline.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed Field class."""

    name: str | None = Field(default=None, max_length=256)
    """Name of the field."""

    value: str | None = Field(default=None, max_length=1024)
    """Value of the field."""

    inline: bool | None = Field(default=None)
    """Whether or not this field should display inline."""


class Embed(BaseModel):
    """
    Represent a Discord Embed of the Rich type.

    https://discord.com/developers/docs/resources/message#embed-object

    Attributes:
        title (str | None): Title of Embed.

        type (EmbedTypes): The value of EmbedTypes.RICH.

        description (str | None): Description of Embed.

        url (str | None): URL of Embed.

        timestamp (str | int | float | datetime | None): Timestamp of Embed content.

        color (str | int | None): Color code of the Embed.

        footer (EmbedFooter | None): Footer information.

        image (EmbedImage | None): Image information.

        thumbnail (EmbedThumbnail | None): Thumbnail information.

        author (EmbedAuthor | None): Author information.

        fields (list[EmbedField] | None): Fields information, max of 25.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Embed class."""

    title: str | None = Field(default=None, max_length=256)
    """Title of Embed."""

    type: EmbedTypes = Field(default=EmbedTypes.RICH, frozen=True)
    """The value of EmbedTypes.RICH."""

    description: str | None = Field(default=None, max_length=4096)
    """Description of Embed."""

    url: str | None = Field(default=None)
    """URL of Embed."""

    timestamp: int | float | str | datetime | None = Field(default=None)
    """Timestamp of Embed content."""

    color: str | int | None = Field(default=None)
    """Color code of the Embed."""

    footer: EmbedFooter | None = Field(default=None)
    """Footer information."""

    image: EmbedImage | None = Field(default=None)
    """Image information."""

    thumbnail: EmbedThumbnail | None = Field(default=None)
    """Thumbnail information."""

    author: EmbedAuthor | None = Field(default=None)
    """Author information."""

    fields: list[EmbedField] | None = Field(default=None, max_length=25)
    """Fields information, max of 25."""

    def set_title(self: Self, title: str | None) -> "Embed":
        """
        Set the title of the Embed.

        Arguments:
            title (str | None): Title of Embed. If set to None, the title is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.title = title

        return self

    def set_description(self: Self, description: str | None) -> "Embed":
        """
        Set the description of the Embed.

        Arguments:
            description (str | None): Description of Embed. If set to None, the description
                is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.description = description

        return self

    def set_url(self: Self, url: str | None) -> "Embed":
        """
        Set the URL of the Embed.

        Arguments:
            url (str | None): URL of Embed. If set to None, the URL is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.url = url

        return self

    def set_timestamp(
        self: Self, timestamp: int | float | str | datetime | None
    ) -> "Embed":
        """
        Set the timestamp of the Embed content.

        Arguments:
            timestamp (str | int | float | datetime | None): Timestamp of Embed content.
                If set to None, the timestamp is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.timestamp = timestamp

        return self

    def set_color(self: Self, color: str | int | None) -> "Embed":
        """
        Set the color code of the Embed.

        Arguments:
            color (str | int | None): Color code of the Embed. If set to None, the color
                is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.color = color

        return self

    def set_footer(self: Self, footer: EmbedFooter | None) -> "Embed":
        """
        Set the footer information of the Embed.

        Arguments:
            footer (EmbedFooter | None): Footer information. If set to None, the footer
                is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.footer = footer

        return self

    def add_image(self: Self, image: EmbedImage | None) -> "Embed":
        """
        Add an image to the Embed.

        Arguments:
            image (EmbedImage | None): Image information. If set to None, the image is
                cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.image = image

        return self

    def set_thumbnail(self: Self, thumbnail: EmbedThumbnail | None) -> "Embed":
        """
        Set the thumbnail information of the Embed.

        Arguments:
            thumbnail (EmbedThumbnail | None): Thumbnail information. If set to None,
                the thumbnail is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.thumbnail = thumbnail

        return self

    def set_author(self: Self, author: EmbedAuthor | None) -> "Embed":
        """
        Set the author information of the Embed.

        Arguments:
            author (EmbedAuthor | None): Author information. If set to None, the author
                is cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        self.author = author

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
        if not self.fields:
            self.fields = []

        if isinstance(field, EmbedField):
            self.fields.append(field)
        else:
            self.fields.extend(field)

        return self

    def remove_field(
        self: Self, field: EmbedField | list[EmbedField] | int | None
    ) -> "Embed":
        """
        Remove one or more fields from the Embed.

        Arguments:
            field (EmbedField | list[EmbedField] | int | None): An Embed Field, list of
                Embed Fields, or an index to remove. If set to None, the fields value is
                cleared.

        Returns:
            self (Embed): The modified Embed instance.
        """
        if self.fields:
            if field:
                if isinstance(field, list):
                    for entry in field:
                        self.fields.remove(entry)
                elif isinstance(field, int):
                    self.fields.pop(field)
                else:
                    self.fields.remove(field)

                # Do not retain an empty list
                if len(self.fields) == 0:
                    self.fields = None
            else:
                self.fields = None

        return self

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str | int:
        """
        Validate the value of color for an Embed.

        Arguments:
            color (str | int): The value to validate.

        Returns:
            color (int): The validated color value.
        """
        return Validation.validate_url_scheme(url, ["http", "https"])

    @field_validator("timestamp", mode="after")
    @classmethod
    def _validate_timestamp(cls, timestamp: int | float | str | datetime) -> str | int:
        """
        Validate the value of timestamp for an Embed.

        Arguments:
            color (str | int): The value to validate.

        Returns:
            color (int): The validated color value.
        """
        return Validation.validate_timestamp(timestamp)

    @field_validator("color", mode="after")
    @classmethod
    def _validate_color(cls, color: str | int) -> str | int:
        """
        Validate the value of color for an Embed.

        Arguments:
            color (str | int): The value to validate.

        Returns:
            color (int): The validated color value.
        """
        return Validation.validate_color(color)
