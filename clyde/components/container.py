"""Define the Container class and its associates."""

from typing import Self, TypeAlias

from pydantic import Field, field_validator

from clyde.component import Component, ComponentTypes
from clyde.components.action_row import ActionRow
from clyde.components.file import File
from clyde.components.media_gallery import MediaGallery
from clyde.components.section import Section
from clyde.components.seperator import Seperator
from clyde.components.text_display import TextDisplay
from clyde.validation import Validation

ContainerComponent: TypeAlias = (
    ActionRow | TextDisplay | Section | MediaGallery | Seperator | File
)


class Container(Component):
    """
    Represent a Discord Component of the Container type.

    A Container is a top-level layout Component. Containers are visually distinct from
    surrounding Components and have an optional customizable color bar.

    https://discord.com/developers/docs/components/reference#container

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.CONTAINER.

        components (list[ContainerComponent]): Components of the type Action Row,
            Text Display, Section, Media Gallery, Separator, or File.

        accent_color (str | int | None): Color for the accent on the Container.

        spoiler (bool | None): Whether the Container should be a spoiler (blurred).
    """

    type: ComponentTypes = Field(default=ComponentTypes.CONTAINER, frozen=True)
    """The value of ComponentTypes.CONTAINER."""

    components: list[ContainerComponent] | None = Field(default=None)
    """Components of the type Action Row, Text Display, Section, Media Gallery, Separator, or File"""

    accent_color: str | int | None = Field(default=None)
    """Color for the accent on the Container."""

    spoiler: bool | None = Field(default=None)
    """Whether the Container should be a spoiler (blurred)."""

    def add_component(
        self: Self, component: ContainerComponent | list[ContainerComponent]
    ) -> "Container":
        """
        Add one or more Components to the Container.

        Arguments:
            component (ContainerComponent | list[ContainerComponent]): A Component or list
                of Components to add to the Container. Components must be of the type
                Action Row, Text Display, Section, Media Gallery, Separator, or File.

        Returns:
            self (Container): The modified Container instance.
        """
        if not self.components:
            self.components = []

        if isinstance(component, list):
            self.components.extend(component)
        else:
            self.components.append(component)

        return self

    def remove_component(
        self: Self,
        component: ContainerComponent | list[ContainerComponent] | int | None,
    ) -> "Container":
        """
        Remove a Component from the Section instance.

        Arguments:
            component (ContainerComponent | list[ContainerComponent] | int | None): A Component,
                list of Components, or an index to remove. If set to None, all Components
                are removed.

        Returns:
            self (Container): The modified Container instance.
        """
        if self.components:
            if component:
                if isinstance(component, list):
                    for entry in component:
                        self.components.remove(entry)
                elif isinstance(component, int):
                    self.components.pop(component)
                else:
                    self.components.remove(component)

                # Do not retain an empty list
                if len(self.components) == 0:
                    self.components = None
            else:
                self.components = None

        return self

    def set_accent_color(self: Self, accent_color: str | int | None) -> "Container":
        """
        Set the color for the accent on the Container.

        Arguments:
            accent_color (str | int): A color, represented as a hexadecimal string
                or an integer, for the accent on the Container. If set to None, the
                accent_color is cleared.

        Returns:
            self (Container): The modified Container instance.
        """
        self.accent_color = accent_color

        return self

    def set_spoiler(self: Self, spoiler: bool | None) -> "Container":
        """
        Set whether the Container should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Container should be a spoiler (blurred). If set
                to None, the spoiler value is cleared.

        Returns:
            self (Container): The modified Container instance.
        """
        self.spoiler = spoiler

        return self

    @field_validator("accent_color", mode="after")
    @classmethod
    def _validate_accent_color(cls, accent_color: str | int) -> str | int:
        """
        Validate the value of accent_color for a Container.

        Arguments:
            accent_color (str | int): The value to validate.

        Returns:
            accent_color (int): The validated accent_color value.
        """
        return Validation.validate_color(accent_color)
