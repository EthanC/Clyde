"""Define the Component class and its associates."""

from enum import IntEnum

from pydantic import BaseModel, ConfigDict, Field


class ComponentTypes(IntEnum):
    """
    Define the available types of Discord Components.

    https://discord.com/developers/docs/components/reference#component-object-component-types

    Attributes:
        ACTION_ROW (int): Container to display a row of interactive Components.

        BUTTON (int): Button object.

        SECTION (int): Container to display text alongside an Accessory Component.

        TEXT_DISPLAY (int): Markdown text.

        THUMBNAIL (int): Small image that can be used as an Accessory.

        MEDIA_GALLERY (int): Display images and other media.

        FILE (int): Displays an attached file.

        SEPERATOR (int): Component to add vertical padding between other Components.

        CONTAINER (int): Container that visually groups a set of Components.
    """

    ACTION_ROW = 1
    """Container to display a row of interactive Components."""

    BUTTON = 2
    """Button object."""

    SECTION = 9
    """Container to display text alongside an Accessory Component."""

    TEXT_DISPLAY = 10
    """Markdown text."""

    THUMBNAIL = 11
    """Small image that can be used as an Accessory."""

    MEDIA_GALLERY = 12
    """Display images and other media."""

    FILE = 13
    """Displays an attached file."""

    SEPERATOR = 14
    """Component to add vertical padding between other Components."""

    CONTAINER = 17
    """Container that visually groups a set of Components."""


class Component(BaseModel):
    """
    Represent a Discord Component.

    Components allow you to style and structure your messages. They are interactive elements
    that can create rich user experiences in your Discord Webhooks.

    https://discord.com/developers/docs/components/reference#what-is-a-component

    Attributes:
        type (ComponentTypes): The type of the Component.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Component class."""

    type: ComponentTypes = Field(...)
    """The type of the Component."""
