"""Define the Media Gallery class and its associates."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem
from clyde.validation import Validation


class MediaGalleryItem(BaseModel):
    """
    Represent a Media Gallery Item to be used within a Media Gallery Component.

    https://discord.com/developers/docs/components/reference#media-gallery-media-gallery-item-structure

    Attributes:
        media (UnfurledMediaItem): A URL or attachment.

        description (str | None): Alt text for the media.

        spoiler (bool | None): Whether the media should be a spoiler (blurred).
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Media Gallery Item class."""

    media: UnfurledMediaItem | None = Field(default=None)
    """A URL or attachment."""

    description: str | None = Field(default=None)
    """Alt text for the media."""

    spoiler: bool | None = Field(default=None)
    """Whether the media should be a spoiler (blurred)."""

    def set_media(self: Self, media: UnfurledMediaItem | str) -> "MediaGalleryItem":
        """
        Set the URL or attachment for the Media Gallery Item.

        Arguments:
            media (UnfurledMediaItem | str): A URL or attachment.

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        if isinstance(media, str):
            media = UnfurledMediaItem(url=media)

        self.media = media

        return self

    def set_description(
        self: Self, description: str | None = None
    ) -> "MediaGalleryItem":
        """
        Set the alt text for the Media Gallery Item.

        Arguments:
            description (str | None): The alt text to set for the Media Gallery Item.
                If set to None, the alt text is cleared.

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.description = description

        return self

    def set_spoiler(self: Self, spoiler: bool | None) -> "MediaGalleryItem":
        """
        Set whether the Media Gallery Item should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Media Gallery Item should be a spoiler (blurred).
                If set to None, the value of spoiler is cleared.

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.spoiler = spoiler

        return self

    @field_validator("media", mode="after")
    @classmethod
    def _validate_media(cls, media: UnfurledMediaItem) -> UnfurledMediaItem:
        """
        Validate the value of media for a Media Gallery Item.

        Arguments:
            media (UnfurledMediaItem): The value to validate.

        Returns:
            media (UnfurledMediaItem): The validated media value.
        """
        return UnfurledMediaItem(
            url=Validation.validate_url_scheme(
                media.url, ["http", "https", "attachment"]
            )
        )


class MediaGallery(Component):
    """
    Represent a Discord Component of the Media Gallery type.

    A Media Gallery is a top-level content Component that allows you to display 1-10 media
    attachments in an organized gallery format. Each item can have optional descriptions
    and can be marked as spoilers.

    https://discord.com/developers/docs/components/reference#media-gallery

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.MEDIA_GALLERY.

        items (list[MediaGalleryItem]): 1 to 10 Media Gallery Items.
    """

    type: ComponentTypes = Field(default=ComponentTypes.MEDIA_GALLERY, frozen=True)
    """The value of ComponentTypes.MEDIA_GALLERY."""

    items: list[MediaGalleryItem] | None = Field(default=None, max_length=10)
    """1 to 10 Media Gallery Items."""

    def add_item(
        self: Self, item: MediaGalleryItem | list[MediaGalleryItem]
    ) -> "MediaGallery":
        """
        Add one or more Media Gallery Items to the Media Gallery.

        Arguments:
            item (MediaGalleryItem | list[MediaGalleryItem]): A Media Gallery Item or
                list of Media Gallery Items to add to the Media Gallery.

        Returns:
            self (MediaGallery): The modified Media Gallery instance.
        """
        if not self.items:
            self.items = []

        if isinstance(item, list):
            self.items.extend(item)
        else:
            self.items.append(item)

        return self

    def remove_item(
        self: Self, item: MediaGalleryItem | list[MediaGalleryItem] | int | None
    ) -> "MediaGallery":
        """
        Remove a Media Gallery Item from the Media Gallery instance.

        Arguments:
            item (MediaGalleryItem | list[MediaGalleryItem] | int | None): A Media Gallery
                Item, list of Media Gallery Items, or an index to remove. If set to None,
                all items are removed.

        Returns:
            self (MediaGallery): The modified Media Gallery instance.
        """
        if self.items:
            if item:
                if isinstance(item, list):
                    for entry in item:
                        self.items.remove(entry)
                elif isinstance(item, int):
                    self.items.pop(item)
                else:
                    self.items.remove(item)

                # Do not retain an empty list
                if len(self.items) == 0:
                    self.items = None
            else:
                self.items = None

        return self
