"""Define the Action Row class and its associates."""

from typing import Self

from pydantic import Field

from clyde.component import Component, ComponentTypes
from clyde.components.button import LinkButton


class ActionRow(Component):
    """
    Represent a Discord Component of the Action Row type.

    An Action Row is a top-level layout component used in messages and modals.
    Action Rows can contain up to 5 contextually grouped Link Buttons.

    https://discord.com/developers/docs/components/reference#action-row

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.ACTION_ROW.

        components (list[LinkButton]): Up to 5 interactive Link Button Components.
    """

    type: ComponentTypes = Field(default=ComponentTypes.ACTION_ROW, frozen=True)
    """The value of ComponentTypes.ACTION_ROW."""

    components: list[LinkButton] | None = Field(default=None, max_length=5)
    """Up to 5 interactive Link Button Components."""

    def add_component(
        self: Self, component: LinkButton | list[LinkButton]
    ) -> "ActionRow":
        """
        Add one or more Link Button Components to the Action Row.

        Arguments:
            component (LinkButton | list[LinkButton]): A Link Button or list of Link Buttons
                to add to the Action Row.

        Returns:
            self (ActionRow): The modified Action Row instance.
        """
        if not self.components:
            self.components = []

        if isinstance(component, list):
            self.components.extend(component)
        else:
            self.components.append(component)

        return self
