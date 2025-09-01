"""Define the Container class and its associates."""

from typing import Annotated, Self, TypeAlias

import msgspec
from msgspec import UNSET, Meta, UnsetType

from clyde.component import Component, ComponentTypes
from clyde.components.action_row import ActionRow
from clyde.components.file import File
from clyde.components.media_gallery import MediaGallery
from clyde.components.section import Section
from clyde.components.seperator import Seperator
from clyde.components.text_display import TextDisplay

ContainerComponent: TypeAlias = (
    ActionRow | TextDisplay | Section | MediaGallery | Seperator | File
)


class Container(Component, kw_only=True):
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

    type: ComponentTypes = msgspec.field(default=ComponentTypes.CONTAINER)
    """The value of ComponentTypes.CONTAINER."""

    components: Annotated[list[ContainerComponent], Meta(min_length=1)] = (
        msgspec.field()
    )
    """Components of the type Action Row, Text Display, Section, Media Gallery, Separator, or File"""

    accent_color: UnsetType | str | int = msgspec.field(default=UNSET)
    """Color for the accent on the Container."""

    spoiler: UnsetType | bool = msgspec.field(default=UNSET)
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
        if isinstance(component, ContainerComponent):
            self.components.append(component)
        else:
            self.components.extend(component)

        return self

    def remove_component(
        self: Self, component: ContainerComponent | list[ContainerComponent] | int
    ) -> "Container":
        """
        Remove a Component from the Section instance.

        Arguments:
            component (ContainerComponent | list[ContainerComponent] | int | None): A Component,
                list of Components, or an index to remove.

        Returns:
            self (Container): The modified Container instance.
        """
        if isinstance(component, ContainerComponent):
            self.components.remove(component)
        elif isinstance(component, int):
            self.components.pop(component)
        else:
            self.components = [
                entry for entry in self.components if entry not in component
            ]

        return self

    def set_accent_color(self: Self, accent_color: str | int) -> "Container":
        """
        Set the color for the accent on the Container.

        Arguments:
            accent_color (str | int): A color, represented as a hexadecimal string
                or an integer, for the accent on the Container.

        Returns:
            self (Container): The modified Container instance.
        """
        self.accent_color = accent_color

        return self

    def remove_accent_color(self: Self) -> "Container":
        """
        Remove the color for the accent from the Container.\

        Returns:
            self (Container): The modified Container instance.
        """
        self.accent_color = UNSET

        return self

    def set_spoiler(self: Self, spoiler: bool) -> "Container":
        """
        Set whether the Container should be a spoiler (blurred).

        Arguments:
            spoiler (bool): True if the Container should be a spoiler (blurred).

        Returns:
            self (Container): The modified Container instance.
        """
        self.spoiler = spoiler

        return self

    def remove_spoiler(self: Self) -> "Container":
        """
        Remove whether the Container should be a spoiler (blurred).

        Returns:
            self (Container): The modified Container instance.
        """
        self.spoiler = UNSET

        return self
