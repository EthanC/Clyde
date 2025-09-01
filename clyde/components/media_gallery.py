"""Define the Media Gallery class and its associates."""

from typing import Annotated, Self

import msgspec
from msgspec import UNSET, Meta, Struct, UnsetType

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem


class MediaGalleryItem(Struct, kw_only=True):
    """
    Represent a Media Gallery Item to be used within a Media Gallery Component.

    https://discord.com/developers/docs/components/reference#media-gallery-media-gallery-item-structure

    Attributes:
        media (UnfurledMediaItem): A URL or attachment.

        description (UnsetType | str): Alt text for the media.

        spoiler (UnsetType | bool): Whether the media should be a spoiler (blurred).
    """

    media: UnfurledMediaItem = msgspec.field()
    """A URL or attachment."""

    description: UnsetType | str = msgspec.field(default=UNSET)
    """Alt text for the media."""

    spoiler: UnsetType | bool = msgspec.field(default=UNSET)
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

    def set_description(self: Self, description: str) -> "MediaGalleryItem":
        """
        Set the alt text for the Media Gallery Item.

        Arguments:
            description (str | None): The alt text to set for the Media Gallery Item.

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.description = description

        return self

    def remove_description(self: Self) -> "MediaGalleryItem":
        """
        Remove the alt text from the Media Gallery Item.

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.description = UNSET

        return self

    def set_spoiler(self: Self, spoiler: bool) -> "MediaGalleryItem":
        """
        Set whether the Media Gallery Item should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Media Gallery Item should be a spoiler (blurred).

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.spoiler = spoiler

        return self

    def remove_spoiler(self: Self) -> "MediaGalleryItem":
        """
        Set whether the Media Gallery Item should be a spoiler (blurred).

        Returns:
            self (MediaGalleryItem): The modified MediaGalleryItem instance.
        """
        self.spoiler = UNSET

        return self


class MediaGallery(Component, kw_only=True):
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

    type: ComponentTypes = msgspec.field(default=ComponentTypes.MEDIA_GALLERY)
    """The value of ComponentTypes.MEDIA_GALLERY."""

    items: Annotated[list[MediaGalleryItem], Meta(min_length=1, max_length=10)] = (
        msgspec.field()
    )
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
        if isinstance(item, MediaGalleryItem):
            self.items.append(item)
        else:
            self.items.extend(item)

        return self

    def remove_item(
        self: Self, item: MediaGalleryItem | list[MediaGalleryItem] | int
    ) -> "MediaGallery":
        """
        Remove a Media Gallery Item from the Media Gallery instance.

        Arguments:
            item (MediaGalleryItem | list[MediaGalleryItem] | int): A Media Gallery Item,
                list of Media Gallery Items, or an index to remove.

        Returns:
            self (MediaGallery): The modified Media Gallery instance.
        """
        if isinstance(item, MediaGalleryItem):
            self.items.remove(item)
        elif isinstance(item, int):
            self.items.pop(item)
        else:
            self.items = [entry for entry in self.items if entry not in item]

        return self
