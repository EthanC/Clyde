"""Define the Section class and its associates."""

from typing import Annotated, Self

import msgspec
from msgspec import Meta

from clyde.component import Component, ComponentTypes
from clyde.components.button import LinkButton
from clyde.components.text_display import TextDisplay
from clyde.components.thumbnail import Thumbnail


class Section(Component, kw_only=True):
    """
    Represent a Discord Component of the Section type.

    A Section is a top-level layout Component that allows you to join text contextually
    with an Accessory.

    https://discord.com/developers/docs/components/reference#section

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.SECTION.

        components (list[TextDisplay]): 1-3 Text Display Components.

        accessory (Thumbnail | LinkButton): A Thumbnail or a Link Button Component.
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.SECTION)
    """The value of ComponentTypes.SECTION."""

    components: Annotated[list[TextDisplay], Meta(min_length=1, max_length=3)] = (
        msgspec.field()
    )
    """1-3 Text Display Components."""

    accessory: Thumbnail | LinkButton = msgspec.field()
    """A Thumbnail or a Link Button Component."""

    def add_component(
        self: Self, component: TextDisplay | list[TextDisplay]
    ) -> "Section":
        """
        Add one or more Text Display Components to the Section instance.

        Arguments:
            component (TextDisplay | list[TextDisplay]): A Text Display or list of
                Text Displays to add to the Section.

        Returns:
            self (Section): The modified Section instance.
        """
        if isinstance(component, TextDisplay):
            self.components.append(component)
        else:
            self.components.extend(component)

        return self

    def remove_component(
        self: Self, component: TextDisplay | list[TextDisplay] | int
    ) -> "Section":
        """
        Remove a Component from the Section instance.

        Arguments:
            component (TextDisplay | list[TextDisplay] | int): A Component, list of
                Components, or an index to remove.

        Returns:
            self (Section): The modified Section instance.
        """
        if isinstance(component, TextDisplay):
            self.components.remove(component)
        elif isinstance(component, int):
            self.components.pop(component)
        else:
            self.components = [
                entry for entry in self.components if entry not in component
            ]

        return self

    def set_accessory(self: Self, accessory: Thumbnail | LinkButton) -> "Section":
        """
        Set the Accessory Component on the Section instance.

        Arguments:
            accessory (Thumbnail | LinkButton): A Thumbnail or Link Button Component to
                set on the Section.

        Returns:
            self (Section): The modified Section instance.
        """
        self.accessory = accessory

        return self
