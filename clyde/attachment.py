"""Define the Attachment class and its associates."""

from pathlib import Path
from typing import Final, Self

import msgspec
from msgspec import UNSET, Struct, UnsetType

SPOILER_PREFIX: Final[str] = "SPOILER_"


class Attachment(Struct, kw_only=True):
    """
    Represent a Discord Attachment.

    https://discord.com/developers/docs/resources/message#attachment-object

    Attributes:
        filename (str): Name of the file attached.

        content (bytes): Binary content of the file attached.

        spoiler (bool | None): Whether the Container should be a spoiler (blurred).
    """

    filename: UnsetType | str = msgspec.field(default=UNSET)
    """Name of file attached."""

    content: UnsetType | bytes = msgspec.field(default=UNSET)
    """Binary content of the file attached."""

    spoiler: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether the file should be a spoiler (blurred)."""

    def set_filename(self: Self, filename: str) -> "Attachment":
        """
        Set the filename of the file Attachment.

        Arguments:
            filename (str): Name of the file.

        Returns:
            self (Attachment): The modified Attachment instance.
        """
        self.filename = filename

        return self

    def set_content(self: Self, content: bytes | Path) -> "Attachment":
        """
        Set the content of the file Attachment.

        Arguments:
            content (bytes | Path): Binary content of the file. If a Path is passed,
                the referenced file will be read.

        Returns:
            self (Attachment): The modified Attachment instance.
        """
        if isinstance(content, Path):
            with open(content, "rb") as handle:
                content = handle.read()

        self.content = content

        return self

    def set_spoiler(self: Self, spoiler: bool) -> "Attachment":
        """
        Toggle whether the file Attachment is a spoiler.

        Arguments:
            spoiler (bool): True if the file should be a spoiler (blurred).

        Returns:
            self (Attachment): The modified Attachment instance.
        """
        self.spoiler = spoiler

        if isinstance(self.filename, str):
            if spoiler and not self.filename.startswith(SPOILER_PREFIX):
                self.set_filename(SPOILER_PREFIX + self.filename)
            elif not spoiler and self.filename.startswith(SPOILER_PREFIX):
                self.set_filename(self.filename.removeprefix(SPOILER_PREFIX))

        return self
