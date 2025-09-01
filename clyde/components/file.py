"""Define the File class and its associates."""

from typing import Self

import msgspec
from msgspec import UNSET, UnsetType

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem


class File(Component, kw_only=True):
    """
    Represent a Discord Component of the File type.

    A File is a top-level Component that allows you to display an uploaded file as an
    attachment to the message and reference it in the Component. Each file Component
    can only display 1 attached file, but you can upload multiple files and add them
    to different file Components within your payload.

    https://discord.com/developers/docs/components/reference#file

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.FILE.

        file (UnfurledMediaItem): This Unfurled Media Item is unique in that it only
            supports attachment references using the attachment://<filename> syntax.

        spoiler (bool | None): Whether the media should be a spoiler (blurred).
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.FILE)
    """The value of ComponentTypes.FILE."""

    file: UnfurledMediaItem = msgspec.field()
    """
    This Unfurled Media Item is unique in that it only supports attachment references
    using the attachment://<filename> syntax.
    """

    spoiler: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether the media should be a spoiler (blurred)."""

    def set_file(self: Self, file: UnfurledMediaItem | str) -> "File":
        """
        Set the file for this component.

        Arguments:
            file (UnfurledMediaItem | str): This Unfurled Media Item is unique in that
                it only supports attachment references using the attachment://<filename>
                syntax.

        Returns:
            self (File): The modified File instance.
        """
        if isinstance(file, str):
            file = UnfurledMediaItem(url=file)

        self.file = file

        return self

    def set_spoiler(self: Self, spoiler: bool) -> "File":
        """
        Set whether the File should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the File should be a spoiler (blurred).

        Returns:
            self (File): The modified File instance.
        """
        self.spoiler = spoiler

        return self

    def remove_spoiler(self: Self) -> "File":
        """
        Remove whether the File should be a spoiler (blurred).

        Returns:
            self (File): The modified File instance.
        """
        self.spoiler = UNSET

        return self
