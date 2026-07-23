"""Define the Action Row class and its associates."""

from typing import Annotated, Self

import msgspec
from msgspec import Meta

from clyde.component import Component, ComponentTypes, _ComponentOwner
from clyde.components.button import LinkButton


class ActionRow(Component, kw_only=True):
    """
    Represent a Discord Component of the Action Row type.

    An Action Row is a top-level layout component used in messages and modals.
    Action Rows can contain up to 5 contextually grouped Link Buttons.

    https://discord.com/developers/docs/components/reference#action-row

    Attributes:
        type (ComponentTypes): The value of ComponentTypes.ACTION_ROW.

        components (list[LinkButton]): Up to 5 interactive Link Button Components.
    """

    type: ComponentTypes = msgspec.field(default=ComponentTypes.ACTION_ROW)
    """The value of ComponentTypes.ACTION_ROW."""

    components: Annotated[list[LinkButton], Meta(min_length=1, max_length=5)] = (
        msgspec.field()
    )
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

        Raises:
            ValueError: The addition would exceed an owning message's 40 total
                Component limit.
        """
        components: list[LinkButton]

        if isinstance(component, LinkButton):
            components = [component]
        else:
            components = list(component)

        owners: list[_ComponentOwner] = self._validate_component_addition(components)
        self.components = [*self.components, *components]

        self._synchronize_component_owners(owners)

        return self

    def remove_component(
        self: Self, component: LinkButton | list[LinkButton] | int
    ) -> "ActionRow":
        """
        Remove one or more Link Button Components from the Action Row.

        Arguments:
            component (LinkButton | list[LinkButton] | int): A Link Button, list of Link Buttons,
                or an index to remove from the Action Row.

        Returns:
            self (ActionRow): The modified Action Row instance.
        """
        owners: list[_ComponentOwner] = self._active_component_owners()
        components: list[LinkButton] = self.components.copy()

        if isinstance(component, LinkButton):
            components.remove(component)
        elif isinstance(component, int):
            components.pop(component)
        else:
            components = [entry for entry in components if entry not in component]

        self.components = components

        self._synchronize_component_owners(owners)

        return self
