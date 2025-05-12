"""Define the Thumbnail class and its associates."""

from typing import Self

from pydantic import Field

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem


class Thumbnail(Component):
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

    type: ComponentTypes = Field(default=ComponentTypes.THUMBNAIL, frozen=True)
    """The value of ComponentTypes.THUMBNAIL."""

    media: UnfurledMediaItem | None = Field(default=None)
    """A URL or attachment."""

    description: str | None = Field(default=None)
    """Alt text for the media."""

    spoiler: bool | None = Field(default=None)
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

    def set_description(self: Self, description: str | None) -> "Thumbnail":
        """
        Set the alt text for the Thumbnail.

        Arguments:
            description (str | None): The alt text to set for the Thumbnail. If set to
                None, the alt text is cleared.

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.description = description

        return self

    def set_spoiler(self: Self, spoiler: bool | None) -> "Thumbnail":
        """
        Set whether the Thumbnail should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Thumbnail should be a spoiler (blurred). If set
                to None, the spoiler value is cleared.

        Returns:
            self (Thumbnail): The modified Thumbnail instance.
        """
        self.spoiler = spoiler

        return self
