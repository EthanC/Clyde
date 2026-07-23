"""Validate message-wide Component limits without making network requests."""

from copy import copy
from gc import collect
from typing import Final, Iterator, cast
from weakref import ReferenceType, ref

import msgspec
import pytest
from msgspec import UNSET, UnsetType

from clyde import TopLevelComponent, Webhook
from clyde.components import (
    ActionRow,
    Container,
    LinkButton,
    MediaGallery,
    MediaGalleryItem,
    Section,
    TextDisplay,
    UnfurledMediaItem,
)
from clyde.components.container import ContainerComponent
from clyde.webhook import MessageFlags

WEBHOOK_URL: Final[str] = "https://discord.com/api/webhooks/1/token"


def text_components(count: int, prefix: str = "Component") -> list[TextDisplay]:
    """Create distinct Text Display Components for limit tests."""
    return [TextDisplay(content=f"{prefix} {index}") for index in range(count)]


def link_button(label: str = "Link") -> LinkButton:
    """Create a Link Button Component for limit tests."""
    return LinkButton(label=label, url="https://discord.com")


def test_top_level_addition_validates_recursive_limit_atomically() -> None:
    """Accept 40 total Components and reject an atomic addition of Component 41."""
    container: Container = Container(
        components=cast(list[ContainerComponent], text_components(39))
    )
    webhook: Webhook = Webhook(url=WEBHOOK_URL)

    assert webhook.add_component(container) is webhook
    assert webhook.get_flag(MessageFlags.IS_COMPONENTS_V2)
    flags: UnsetType | None | int = webhook.flags

    with pytest.raises(ValueError, match="40 total Components"):
        webhook.add_component(TextDisplay(content="Too many"))

    assert webhook.components == [container]
    assert webhook.flags == flags

    rejected: Webhook = Webhook(url=WEBHOOK_URL)
    additions: Iterator[TextDisplay] = (
        TextDisplay(content=f"Generated {index}") for index in range(41)
    )

    with pytest.raises(ValueError, match="40 total Components"):
        rejected.add_component(additions)

    assert rejected.components is UNSET
    assert rejected.flags is UNSET


def test_component_count_includes_accessories_but_not_gallery_items() -> None:
    """Count Section accessories while treating a Media Gallery as one Component."""
    section: Section = Section(
        components=[TextDisplay(content="Section")], accessory=link_button()
    )
    section_webhook: Webhook = Webhook(url=WEBHOOK_URL)
    section_webhook.add_component([*text_components(37), section])
    section.set_accessory(link_button("Replacement"))

    with pytest.raises(ValueError, match="40 total Components"):
        section_webhook.add_component(TextDisplay(content="Too many"))

    gallery: MediaGallery = MediaGallery(
        items=[
            MediaGalleryItem(
                media=UnfurledMediaItem(url=f"https://example.com/{index}")
            )
            for index in range(10)
        ]
    )
    gallery_webhook: Webhook = Webhook(url=WEBHOOK_URL)

    assert (
        gallery_webhook.add_component([*text_components(39), gallery])
        is gallery_webhook
    )

    with pytest.raises(ValueError, match="40 total Components"):
        gallery_webhook.add_component(TextDisplay(content="Too many"))


@pytest.mark.parametrize(
    ("parent", "addition", "filler_count"),
    [
        (ActionRow(components=[link_button()]), link_button("Second"), 38),
        (
            Container(components=[TextDisplay(content="Container")]),
            TextDisplay(content="Second"),
            38,
        ),
        (
            Section(
                components=[TextDisplay(content="Section")], accessory=link_button()
            ),
            TextDisplay(content="Second"),
            37,
        ),
    ],
    ids=("action-row", "container", "section"),
)
def test_attached_nested_addition_is_atomic(
    parent: ActionRow | Container | Section,
    addition: LinkButton | TextDisplay,
    filler_count: int,
) -> None:
    """Reject nested additions against the owning message's complete tree."""
    webhook: Webhook = Webhook(url=WEBHOOK_URL)
    webhook.add_component([parent, *text_components(filler_count)])
    component_count: int = len(parent.components)

    with pytest.raises(ValueError, match="40 total Components"):
        if isinstance(parent, ActionRow):
            assert isinstance(addition, LinkButton)
            parent.add_component(addition)
        elif isinstance(parent, Container):
            assert isinstance(addition, TextDisplay)
            parent.add_component(addition)
        else:
            assert isinstance(addition, TextDisplay)
            parent.add_component(addition)

    assert len(parent.components) == component_count


def test_removals_reclaim_component_capacity() -> None:
    """Recompute available capacity after nested, bulk, and complete removals."""
    container: Container = Container(
        components=cast(list[ContainerComponent], text_components(38, "Nested"))
    )
    sibling: TextDisplay = TextDisplay(content="Sibling")
    webhook: Webhook = Webhook(url=WEBHOOK_URL)
    webhook.add_component([container, sibling])

    removed_children: list[ContainerComponent] = container.components[:2]
    container.remove_component(removed_children)
    container.add_component(
        cast(list[ContainerComponent], text_components(2, "Replacement"))
    )

    with pytest.raises(ValueError, match="40 total Components"):
        container.add_component(TextDisplay(content="Too many"))

    container.remove_component(0)
    assert (
        container.add_component(TextDisplay(content="Index replacement")) is container
    )

    webhook.remove_component(sibling)
    replacement_sibling: TextDisplay = TextDisplay(content="Replacement sibling")
    assert webhook.add_component(replacement_sibling) is webhook

    with pytest.raises(ValueError, match="40 total Components"):
        webhook.add_component(TextDisplay(content="Too many"))

    assert webhook.remove_component(None) is webhook
    assert webhook.components == []
    webhook.add_component(text_components(40, "Reset"))
    assert isinstance(webhook.components, list)

    removed_components: list[TopLevelComponent] = webhook.components[:2]
    webhook.remove_component(removed_components)
    webhook.add_component(text_components(2, "Bulk replacement"))

    with pytest.raises(ValueError, match="40 total Components"):
        webhook.add_component(TextDisplay(content="Too many"))


def test_shared_component_removal_updates_each_owner() -> None:
    """Release one message owner without detaching a shared Component from another."""
    container: Container = Container(components=[TextDisplay(content="Shared")])
    full: Webhook = Webhook(url=WEBHOOK_URL)
    roomy: Webhook = Webhook(url=WEBHOOK_URL)
    full.add_component([container, *text_components(38, "Full")])
    roomy.add_component(container)

    with pytest.raises(ValueError, match="40 total Components"):
        container.add_component(TextDisplay(content="Blocked"))

    assert full.remove_component(container) is full
    assert container.add_component(TextDisplay(content="Allowed")) is container
    assert full.add_component(text_components(2, "Reclaimed")) is full
    assert "_clyde_webhook_owners" not in msgspec.to_builtins(container)
    assert "_clyde_owned_components" not in msgspec.to_builtins(roomy)


def test_shared_child_lists_use_copy_on_write_mutations() -> None:
    """Avoid changing another parent when their initial child lists are shared."""
    shared_components: list[ContainerComponent] = [TextDisplay(content="Shared child")]
    full_container: Container = Container(components=shared_components)
    roomy_container: Container = Container(components=shared_components)
    full: Webhook = Webhook(url=WEBHOOK_URL)
    roomy: Webhook = Webhook(url=WEBHOOK_URL)
    full.add_component([full_container, *text_components(38, "Full")])
    roomy.add_component(roomy_container)

    assert roomy_container.add_component(TextDisplay(content="Roomy addition"))
    assert len(roomy_container.components) == 2
    assert full_container.components == shared_components

    removable_components: list[ContainerComponent] = [
        TextDisplay(content="Removable child")
    ]
    retained_container: Container = Container(components=removable_components)
    changed_container: Container = Container(components=removable_components)
    retained: Webhook = Webhook(url=WEBHOOK_URL).add_component(retained_container)
    changed: Webhook = Webhook(url=WEBHOOK_URL).add_component(changed_container)

    changed_container.remove_component(0)
    assert len(changed_container.components) == 0
    assert retained_container.components == removable_components
    assert retained is not changed


def test_shallow_webhook_copy_rebuilds_ownership_and_detaches_root_list() -> None:
    """Keep copied Webhooks in nested validation without sharing root mutations."""
    container: Container = Container(components=[TextDisplay(content="Copied")])
    original: Webhook = Webhook(url=WEBHOOK_URL)
    original.add_component([container, *text_components(38, "Original")])
    copied: Webhook = copy(original)
    assert isinstance(copied.components, list)
    copied.remove_component(-1)
    copied.add_component(TextDisplay(content="Copy replacement"))

    assert isinstance(original.components, list)
    assert copied.components is not original.components
    assert original.components[-1] != copied.components[-1]

    original_reference: ReferenceType[Webhook] = ref(original)
    del original
    collect()
    assert original_reference() is None

    with pytest.raises(ValueError, match="40 total Components"):
        container.add_component(TextDisplay(content="Too many"))


def test_repeated_component_occurrences_apply_each_count_change() -> None:
    """Multiply a nested addition by every occurrence of the shared parent."""
    container: Container = Container(components=[TextDisplay(content="Repeated")])
    webhook: Webhook = Webhook(url=WEBHOOK_URL)
    webhook.add_component([container, container, *text_components(35)])

    with pytest.raises(ValueError, match="40 total Components"):
        container.add_component(TextDisplay(content="Adds two occurrences"))

    webhook.remove_component(container)
    assert (
        container.add_component(TextDisplay(content="Adds one occurrence")) is container
    )
    assert webhook.add_component(text_components(2, "Final")) is webhook


def test_pre_send_validation_catches_direct_component_mutation() -> None:
    """Retain a pre-request fallback for mutations that bypass helper methods."""
    webhook: Webhook = Webhook(url=WEBHOOK_URL)
    webhook.add_component(text_components(40))
    assert isinstance(webhook.components, list)
    webhook.components.append(TextDisplay(content="Direct mutation"))

    with pytest.raises(ValueError, match="40 total Components"):
        webhook._validate()


def test_stale_and_expired_component_owners_do_not_restrict_additions() -> None:
    """Ignore owners that no longer contain the Component or no longer exist."""
    detached: Container = Container(components=[TextDisplay(content="Detached")])
    webhook: Webhook = Webhook(url=WEBHOOK_URL)
    webhook.add_component(detached)
    webhook.components = UNSET

    assert detached.add_component(TextDisplay(content="Allowed")) is detached
    assert webhook.__dict__["_clyde_owned_components"] == []

    orphan: Container = Container(components=[TextDisplay(content="Orphan")])
    owner: Webhook = Webhook(url=WEBHOOK_URL)
    owner.add_component(orphan)
    owner_reference: ReferenceType[Webhook] = ref(owner)
    del owner
    collect()

    assert owner_reference() is None
    assert orphan.add_component(TextDisplay(content="Allowed")) is orphan

    leaf: TextDisplay = TextDisplay(content="Reusable leaf")
    expired: Webhook = Webhook(url=WEBHOOK_URL).add_component(leaf)
    del expired
    collect()
    assert leaf.__dict__["_clyde_webhook_owners"] == []

    current: Webhook = Webhook(url=WEBHOOK_URL).add_component(leaf)

    assert len(leaf.__dict__["_clyde_webhook_owners"]) == 1
    assert current.components == [leaf]


def test_direct_detachment_does_not_retain_component_tree() -> None:
    """Keep ownership snapshots from retaining directly detached Components."""
    component: Container = Container(components=[TextDisplay(content="Detached tree")])
    webhook: Webhook = Webhook(url=WEBHOOK_URL).add_component(component)
    component_reference: ReferenceType[Container] = ref(component)
    webhook.components = UNSET
    del component
    collect()

    assert component_reference() is None
    webhook._sync_component_owners()
    assert webhook.__dict__["_clyde_owned_components"] == []


def test_legacy_owner_does_not_apply_components_v2_limit() -> None:
    """Keep legacy Action Row ownership separate from Components V2 validation."""
    action_row: ActionRow = ActionRow(components=[link_button()])
    webhook: Webhook = Webhook(url=WEBHOOK_URL, components=[action_row])

    assert action_row.add_component(link_button("Second")) is action_row
    assert not webhook.get_flag(MessageFlags.IS_COMPONENTS_V2)
