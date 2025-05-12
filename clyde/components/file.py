"""Define the File class and its associates."""

from typing import Self

from pydantic import Field, field_validator

from clyde.component import Component, ComponentTypes
from clyde.components.unfurled_media_item import UnfurledMediaItem
from clyde.validation import Validation


class File(Component):
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

    type: ComponentTypes = Field(default=ComponentTypes.FILE, frozen=True)
    """The value of ComponentTypes.FILE."""

    file: UnfurledMediaItem | None = Field(default=None)
    """
    This Unfurled Media Item is unique in that it only supports attachment references
    using the attachment://<filename> syntax.
    """

    spoiler: bool | None = Field(default=None)
    """Whether the media should be a spoiler (blurred)."""

    def set_file(self: Self, file: UnfurledMediaItem | str | None) -> "File":
        """
        Set the file for this component.

        Arguments:
            file (UnfurledMediaItem | str): This Unfurled Media Item is unique in that
                it only supports attachment references using the attachment://<filename>
                syntax. If set to None, the File value is cleared.

        Returns:
            self (File): The modified File instance.
        """
        if isinstance(file, str):
            file = UnfurledMediaItem(url=file)

        self.file = file

        return self

    def set_spoiler(self: Self, spoiler: bool | None) -> "File":
        """
        Set whether the File should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the File should be a spoiler (blurred). If set to
                None, the Spoiler value is cleared.

        Returns:
            self (File): The modified File instance.
        """
        self.spoiler = spoiler

        return self

    @field_validator("file", mode="after")
    @classmethod
    def _validate_file(cls, file: UnfurledMediaItem) -> UnfurledMediaItem:
        """
        Validate the value of file for a File.

        Arguments:
            file (UnfurledMediaItem | str): The value to validate.

        Returns:
            file (UnfurledMediaItem): The validated file value.
        """
        return UnfurledMediaItem(
            url=Validation.validate_url_scheme(file.url, ["attachment"])
        )
