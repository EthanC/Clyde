"""Define the Button class and its associates."""

from enum import IntEnum
from typing import Annotated, Self

import msgspec
from msgspec import Meta

from clyde.component import Component, ComponentTypes


class ButtonStyles(IntEnum):
    """
    Define the available styles of a Button Component.

    https://discord.com/developers/docs/components/reference#button-button-styles

    Attributes:
        LINK (int): Navigates to a URL.
    """

    LINK = 5
    """Navigates to a URL."""


class Button(Component, kw_only=True):
    """
    Represent a Button, an interactive Component that can only be used in messages.

    A Button creates clickable elements that users can interact with. Buttons must be placed
    inside an Action Row or a Section's Accessory field.

    https://discord.com/developers/docs/components/reference#button

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.BUTTON.

        style (ButtonStyles): A Button Style.
    """

    type: ComponentTypes
    """The value of ComponentTypes.BUTTON."""

    style: ButtonStyles
    """A Button Style."""

    def set_style(self: Self, style: ButtonStyles) -> "Button":
        """
        Set the style of the Button.

        Arguments:
            style (ButtonStyles): A style for the Button.

        Returns:
            self (Button): The modified Button instance.
        """
        self.style = style

        return self


class LinkButton(Button, kw_only=True):
    """
    Represent a Button Component navigates to a URL.

    https://discord.com/developers/docs/components/reference#button

    Attributes:
        style (ButtonStyles): The value of ButtonStyles.LINK.

        label (str): Text that appears on the Button; max 80 characters.

        url (str): URL for link-style Buttons.
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.BUTTON)
    """The value of ComponentTypes.BUTTON."""

    style: ButtonStyles = msgspec.field(default=ButtonStyles.LINK)
    """The value of ButtonStyles.LINK."""

    label: Annotated[str, Meta(min_length=1, max_length=80)] = msgspec.field()
    """Text that appears on the Button; max 80 characters."""

    url: str = msgspec.field()
    """URL for link-style Buttons."""

    def set_label(self: Self, label: str) -> "LinkButton":
        """
        Set the label of the Link Button.

        Arguments:
            label (str): Text that appears on the Button; max 80 characters.

        Returns:
            self (LinkButton): The modified Link Button instance.
        """
        self.label = label

        return self

    def set_url(self: Self, url: str) -> "LinkButton":
        """
        Set the URL of the Link Button.

        Arguments:
            url (str): URL for the link-style Button.

        Returns:
            self (LinkButton): The modified Link Button instance.
        """
        self.url = url

        return self
