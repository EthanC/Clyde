"""Define the Button class and its associates."""

from enum import IntEnum
from typing import Self

from pydantic import Field, field_validator

from clyde.component import Component, ComponentTypes
from clyde.validation import Validation


class ButtonStyles(IntEnum):
    """
    Define the available styles of a Button Component.

    https://discord.com/developers/docs/components/reference#button-button-styles

    Attributes:
        LINK (int): Navigates to a URL.
    """

    LINK = 5
    """Navigates to a URL."""


class Button(Component):
    """
    Represent a Button, an interactive Component that can only be used in messages.

    A Button creates clickable elements that users can interact with. Buttons must be placed
    inside an Action Row or a Section's Accessory field.

    https://discord.com/developers/docs/components/reference#button

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.BUTTON.

        style (ButtonStyles): A Button Style.
    """

    type: ComponentTypes = Field(default=ComponentTypes.BUTTON, frozen=True)
    """The value of ComponentTypes.BUTTON."""

    style: ButtonStyles = Field(...)
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


class LinkButton(Button):
    """
    Represent a Button Component navigates to a URL.

    https://discord.com/developers/docs/components/reference#button

    Attributes:
        style (ButtonStyles): The value of ButtonStyles.LINK.

        label (str): Text that appears on the Button; max 80 characters.

        url (str): URL for link-style Buttons.
    """

    style: ButtonStyles = Field(default=ButtonStyles.LINK, frozen=True)
    """The value of ButtonStyles.LINK."""

    label: str | None = Field(default=None, max_length=80)
    """Text that appears on the Button; max 80 characters."""

    url: str | None = Field(default=None)
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

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """
        Validate the value of URL for a Link Button.

        Arguments:
            url (str): The value to validate.

        Returns:
            url (str): The validated URL value.
        """
        return Validation.validate_url_scheme(url, ["http", "https"])
