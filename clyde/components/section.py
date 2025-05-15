"""Define the Section class and its associates."""

from typing import Self

from pydantic import Field

from clyde.component import Component, ComponentTypes
from clyde.components.button import LinkButton
from clyde.components.text_display import TextDisplay
from clyde.components.thumbnail import Thumbnail


class Section(Component):
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

    type: ComponentTypes = Field(default=ComponentTypes.SECTION, frozen=True)
    """The value of ComponentTypes.SECTION."""

    components: list[TextDisplay] | None = Field(default=None, max_length=3)
    """1-3 Text Display Components."""

    accessory: Thumbnail | LinkButton | None = Field(default=None)
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
        if not self.components:
            self.components = []

        if isinstance(component, list):
            self.components.extend(component)
        else:
            self.components.append(component)

        return self

    def remove_component(
        self: Self, component: TextDisplay | list[TextDisplay] | int | None
    ) -> "Section":
        """
        Remove a Component from the Section instance.

        Arguments:
            component (TextDisplay | list[TextDisplay] | int | None): A Component, list
                of Components, or an index to remove. If set to None, all Components
                are removed.

        Returns:
            self (Section): The modified Section instance.
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

    def set_accessory(
        self: Self, accessory: Thumbnail | LinkButton | None
    ) -> "Section":
        """
        Set the Accessory Component on the Section instance.

        Arguments:
            accessory (Thumbnail | LinkButton): A Thumbnail or Link Button Component to
                set on the Section. If set to None, the Accessory value is cleared.

        Returns:
            self (Section): The modified Section instance.
        """
        self.accessory = accessory

        return self

    def remove_accessory(self: Self) -> "Section":
        """
        Remove the Accessory Component from the Section instance.

        Returns:
            self (Section): The modified Section instance.
        """
        self.accessory = None

        return self
