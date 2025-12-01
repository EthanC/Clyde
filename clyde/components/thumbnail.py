"""Define the Thumbnail class and its associates."""

from typing import Self

import msgspec
from msgspec import UNSET, UnsetType

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem


class Thumbnail(Component, kw_only=True, tag="Thumbnail"):
    """
    Represent a Discord Component of the Thumbnail type.

    A Thumbnail is a content Component that is a small image only usable as an Accessory
    in a Section. The preview comes from an Unfurled Media Item.

    https://discord.com/developers/docs/components/reference#thumbnail

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.THUMBNAIL.

        media (UnfurledMediaItem): A URL or attachment.

        description (str | None): Alt text for the media.

        spoiler (bool | None): Whether the Thumbnail should be a spoiler (blurred).
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.THUMBNAIL)
    """The value of ComponentTypes.THUMBNAIL."""

    media: UnfurledMediaItem = msgspec.field()
    """A URL or attachment."""

    description: UnsetType | str = msgspec.field(default=UNSET)
    """Alt text for the media."""

    spoiler: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether the Thumbnail should be a spoiler (blurred)."""

    def set_media(self: Self, media: UnfurledMediaItem | str) -> "Thumbnail":
        """
        Set the URL or attachment for the Thumbnail.

        Arguments:
            media (UnfurledMediaItem | str): A URL or attachment.

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        if isinstance(media, str):
            media = UnfurledMediaItem(url=media)

        self.media = media

        return self

    def set_description(self: Self, description: str) -> "Thumbnail":
        """
        Set the alt text for the Thumbnail.

        Arguments:
            description (str | None): The alt text to set for the Thumbnail.

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.description = description

        return self

    def remove_description(self: Self) -> "Thumbnail":
        """
        Remove the alt text from the Thumbnail.

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.description = UNSET

        return self

    def set_spoiler(self: Self, spoiler: bool) -> "Thumbnail":
        """
        Set whether the Thumbnail should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Thumbnail should be a spoiler (blurred).

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.spoiler = spoiler

        return self

    def remove_spoiler(self: Self) -> "Thumbnail":
        """
        Remove whether the Thumbnail should be a spoiler (blurred).

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.spoiler = UNSET

        return self
