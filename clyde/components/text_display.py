"""Define the Text Display class and its associates."""

from typing import Self

from pydantic import Field

from clyde.component import Component, ComponentTypes


class TextDisplay(Component):
    """
    Represent a Discord Component of the Text Display type.

    A Text Display is a top-level content Component that allows you to add text to your
    message formatted with markdown and mention users and roles. This is similar to the
    content field of a message, but allows you to add multiple text Components, controlling
    the layout of your message.

    https://discord.com/developers/docs/components/reference#text-display

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.TEXT_DISPLAY.

        content (str): Text that will be displayed similar to a message.
    """

    type: ComponentTypes = Field(default=ComponentTypes.TEXT_DISPLAY, frozen=True)
    """The value of ComponentTypes.TEXT_DISPLAY."""

    content: str | None = Field(default=None)
    """Text that will be displayed similar to a message."""

    def set_content(self: Self, content: str) -> "TextDisplay":
        """
        Set the text that will be displayed on the Text Display.

        Arguments:
            content (str): The text that will be displayed similar to a message.

        Returns:
            self (TextDisplay): The modified Text Display instance.
        """
        self.content = content

        return self
