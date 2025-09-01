"""Define the Seperator class and its associates."""

from enum import IntEnum
from typing import Self

import msgspec
from msgspec import UNSET, UnsetType

from clyde.component import Component, ComponentTypes


class SeperatorSpacing(IntEnum):
    """
    An enumeration representing the size of the Separator's padding.

    The SeperatorSpacing enum defines two possible values for the padding size:
    SMALL (1) and LARGE (2).

    Attributes:
        SMALL (int): The smaller padding size.

        LARGE (int): The larger padding size.
    """

    SMALL = 1
    """Small padding."""

    LARGE = 2
    """Large padding."""


class Seperator(Component, kw_only=True):
    """
    Represent a Discord Component of the Seperator type.

    A Separator is a top-level layout Component that adds vertical padding and visual
    division between other Components.

    https://discord.com/developers/docs/components/reference#separator

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.SEPERATOR.

        divider (bool | None): Whether a visual divider should be displayed in the Component.

        spacing (SeperatorSpacing | None): Size of Separator padding.
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.SEPERATOR)
    """The value of ComponentTypes.SEPERATOR."""

    divider: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether a visual divider should be displayed in the Component."""

    spacing: UnsetType | SeperatorSpacing = msgspec.field(default=UNSET)
    """Size of Separator padding."""

    def set_divider(self: Self, divider: bool) -> "Seperator":
        """
        Set whether a visual divider should be displayed in the Component.

        Arguments:
            divider (bool): True if a visual divider should be displayed in the Component.

        Returns:
            self (Seperator): The modified Seperator instance.
        """
        self.divider = divider

        return self

    def remove_divider(self: Self) -> "Seperator":
        """
        Remove whether a visual divider should be displayed in the Component.

        Returns:
            self (Seperator): The modified Seperator instance.
        """
        self.divider = UNSET

        return self

    def set_spacing(self: Self, spacing: SeperatorSpacing) -> "Seperator":
        """
        Set the size of the padding on the Seperator.

        Arguments:
            spacing (SeperatorSpacing): The size of the padding on the Seperator.

        Returns:
            self (Seperator): The modified Seperator instance.
        """
        self.spacing = spacing

        return self

    def remove_spacing(self: Self) -> "Seperator":
        """
        Remove the size of the padding from the Seperator.

        Returns:
            self (Seperator): The modified Seperator instance.
        """
        self.spacing = UNSET

        return self
