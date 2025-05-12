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
        Add one or more Text Display Components to the Section.

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

    def set_accessory(
        self: Self, accessory: Thumbnail | LinkButton | None
    ) -> "Section":
        """
        Set the Accessory Component on the Section.

        Arguments:
            accessory (Thumbnail | LinkButton): A Thumbnail or Link Button Component to
                set on the Section. If set to None, the Accessory value is cleared.

        Returns:
            self (Section): The modified Section instance.
        """
        self.accessory = accessory

        return self
