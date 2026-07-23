"""Define the Component class and its associates."""

from enum import IntEnum
from functools import partial
from typing import Callable, Final, Iterable, Iterator, Protocol, Self, cast
from weakref import ReferenceType, ref

import msgspec
from msgspec import Struct

_COMPONENT_OWNERS_KEY: Final[str] = "_clyde_webhook_owners"


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


class _ComponentOwner(Protocol):
    """Define Webhook operations used for Component ownership tracking."""

    def _component_occurrences(self: Self, component: "Component") -> int: ...

    def _validate_nested_component_addition(
        self: Self, parent: "Component", components: Iterable["Component"]
    ) -> None: ...

    def _sync_component_owners(self: Self) -> None: ...


class Component(Struct, kw_only=True, tag_field="_type", dict=True, weakref=True):
    """
    Represent a Discord Component.

    Components allow you to style and structure your messages. They are interactive elements
    that can create rich user experiences in your Discord Webhooks.

    https://discord.com/developers/docs/components/reference#what-is-a-component

    Attributes:
        type (ComponentTypes): The type of the Component.
    """

    type: ComponentTypes = msgspec.field()
    """The type of the Component."""

    def _active_component_owners(self: Self) -> list[_ComponentOwner]:
        """Return Webhooks that still contain this Component."""
        references: list[ReferenceType[_ComponentOwner]] = _component_owner_references(
            self
        )
        active_references: list[ReferenceType[_ComponentOwner]] = []
        owners: list[_ComponentOwner] = []
        stale_owners: list[_ComponentOwner] = []

        for reference in references:
            owner: _ComponentOwner = cast(_ComponentOwner, reference())

            if owner._component_occurrences(self) == 0:
                stale_owners.append(owner)

                continue

            active_references.append(reference)
            owners.append(owner)

        references[:] = active_references

        for owner in stale_owners:
            owner._sync_component_owners()

        return owners

    def _validate_component_addition(
        self: Self, components: Iterable["Component"]
    ) -> list[_ComponentOwner]:
        """Validate an addition against every message containing this Component."""
        owners: list[_ComponentOwner] = self._active_component_owners()

        for owner in owners:
            owner._validate_nested_component_addition(self, components)

        return owners

    @staticmethod
    def _synchronize_component_owners(owners: Iterable[_ComponentOwner]) -> None:
        """Synchronize owner membership after a nested Component mutation."""
        for owner in owners:
            owner._sync_component_owners()


def _iter_components(components: Iterable[Component]) -> Iterator[Component]:
    """Iterate over every Component occurrence in one or more Component trees."""
    for component in components:
        yield component

        children: list[Component] | None = cast(
            list[Component] | None, getattr(component, "components", None)
        )

        if isinstance(children, list):
            yield from _iter_components(children)

        accessory: Component | None = cast(
            Component | None, getattr(component, "accessory", None)
        )

        if isinstance(accessory, Component):
            yield from _iter_components([accessory])


def _count_components(components: Iterable[Component]) -> int:
    """Count every Component occurrence in one or more Component trees."""
    return sum(1 for _ in _iter_components(components))


def _count_component_occurrences(
    components: Iterable[Component], target: Component
) -> int:
    """Count identity-based occurrences of a Component in one or more trees."""
    return sum(component is target for component in _iter_components(components))


def _component_owner_references(
    component: Component,
) -> list[ReferenceType[_ComponentOwner]]:
    """Return the non-serialized owner references for a Component."""
    references: list[ReferenceType[_ComponentOwner]] = cast(
        list[ReferenceType[_ComponentOwner]],
        component.__dict__.setdefault(_COMPONENT_OWNERS_KEY, []),
    )

    return references


def _register_component_owner(
    components: Iterable[Component], owner: _ComponentOwner
) -> None:
    """Register a Webhook as an owner of flattened Components."""
    for component in components:
        references: list[ReferenceType[_ComponentOwner]] = _component_owner_references(
            component
        )
        references[:] = [
            reference for reference in references if reference() is not None
        ]

        if not any(reference() is owner for reference in references):
            component_reference: ReferenceType[Component] = ref(component)
            remove_owner: Callable[[ReferenceType[_ComponentOwner]], None] = partial(
                _remove_expired_component_owner, component_reference=component_reference
            )
            owner_reference: ReferenceType[_ComponentOwner] = ref(owner, remove_owner)

            references.append(owner_reference)


def _unregister_component_owner(
    components: Iterable[Component], owner: _ComponentOwner
) -> None:
    """Unregister a Webhook as an owner of flattened Components."""
    for component in components:
        references: list[ReferenceType[_ComponentOwner]] = _component_owner_references(
            component
        )
        references[:] = [
            reference for reference in references if reference() is not owner
        ]


def _remove_expired_component_owner(
    owner_reference: ReferenceType[_ComponentOwner],
    component_reference: ReferenceType[Component],
) -> None:
    """Remove an expired Webhook reference from a live Component."""
    component: Component = cast(Component, component_reference())
    references: list[ReferenceType[_ComponentOwner]] = _component_owner_references(
        component
    )
    references[:] = [
        reference for reference in references if reference is not owner_reference
    ]
