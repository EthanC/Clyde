from time import sleep

import pytest
from msgspec import UNSET
from niquests import Response

from clyde import Webhook
from clyde.components import (
    ActionRow,
    Container,
    File,
    LinkButton,
    MediaGallery,
    MediaGalleryItem,
    Section,
    Seperator,
    SeperatorSpacing,
    TextDisplay,
    Thumbnail,
    UnfurledMediaItem,
)
from clyde.components.button import ButtonStyles
from clyde.components.container import ContainerComponent

from .constants import (
    FLOAT_TEST_DELAY,
    STRING_COLOR_BLACK,
    STRING_EXTRA_LONG,
    STRING_EXTRA_SHORT,
    STRING_LONG,
    STRING_LONG_MARKDOWN,
    STRING_MEDIUM,
    STRING_SHORT,
    STRING_URL_DISCORD,
    STRING_URL_GITHUB,
    STRING_URL_ICON_1,
    STRING_URL_ICON_2,
    STRING_URL_ICON_3,
    STRING_URL_ICON_4,
    STRING_URL_IMAGE_1,
    STRING_URL_IMAGE_2,
    STRING_URL_IMAGE_3,
    STRING_URL_IMAGE_4,
    STRING_URL_WEBHOOK,
    STRING_WORD,
)


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def test_component_action_row() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with an Action Row
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    action_row: ActionRow = ActionRow(components=[])

    action_row.add_component(
        LinkButton(label=STRING_EXTRA_SHORT, url=STRING_URL_GITHUB)
    )
    webhook.add_component(action_row)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


@pytest.mark.xfail
def test_component_action_row_empty() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with an empty
    Action Row Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    action_row: ActionRow = ActionRow(components=[])

    webhook.add_component(action_row)

    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to no Components within Action Row
    assert isinstance(res, Response) and res.ok


def test_component_link_button() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Link Button
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    action_row: ActionRow = ActionRow(components=[])
    button: LinkButton = LinkButton(label=STRING_WORD, url=STRING_URL_GITHUB)

    button.set_label(STRING_WORD)
    button.set_url(STRING_URL_DISCORD)
    action_row.add_component(button)
    webhook.add_component(action_row)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_container() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Container
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    container: Container = Container(components=[])
    body: TextDisplay = TextDisplay(content=STRING_WORD)

    body.set_content(STRING_LONG)
    container.set_spoiler(True)
    container.set_accent_color(STRING_COLOR_BLACK)
    container.add_component(body)
    webhook.add_component(container)

    container.add_component(TextDisplay(content=STRING_EXTRA_LONG))
    container.remove_component(-1)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_media_gallery() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Media Gallery
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    gallery: MediaGallery = MediaGallery(items=[])

    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_1), description=STRING_LONG
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_2),
            description=STRING_MEDIUM,
            spoiler=False,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_3),
            description=STRING_SHORT,
            spoiler=True,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_4),
            description=STRING_EXTRA_SHORT,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_1), description=STRING_LONG
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_ICON_1),
            description=STRING_MEDIUM,
            spoiler=False,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_IMAGE_3),
            description=STRING_SHORT,
            spoiler=True,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_ICON_2),
            description=STRING_EXTRA_SHORT,
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_ICON_3), description=STRING_LONG
        )
    )
    gallery.add_item(
        MediaGalleryItem(
            media=UnfurledMediaItem(url=STRING_URL_ICON_4),
            description=STRING_MEDIUM,
            spoiler=False,
        )
    )
    webhook.add_component(gallery)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_section() -> None:
    """A test-case to validate the creation and execution of a Webhook with a Section Component."""

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    section: Section = Section(
        components=[], accessory=LinkButton(label=STRING_WORD, url=STRING_URL_DISCORD)
    )

    section.add_component(TextDisplay(content=STRING_SHORT))
    section.add_component(TextDisplay(content=STRING_MEDIUM))

    bad_text: TextDisplay = TextDisplay(content=STRING_EXTRA_LONG)
    section.add_component(bad_text)
    section.remove_component(bad_text)

    section.add_component(TextDisplay(content=STRING_LONG))

    section.set_accessory(LinkButton(label=STRING_EXTRA_SHORT, url=STRING_URL_GITHUB))

    webhook.add_component(section)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_seperator() -> None:
    """A test-case to validate the creation and execution of a Webhook with a Seperator Component."""

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    seperator: Seperator = Seperator()

    seperator.set_divider(True)
    seperator.set_spacing(SeperatorSpacing.LARGE)
    webhook.add_component(TextDisplay(content=STRING_SHORT))
    webhook.add_component(seperator)
    webhook.add_component(TextDisplay(content=STRING_SHORT))

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_text_display() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Text Display
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    text_display: TextDisplay = TextDisplay(content=STRING_WORD)

    text_display.set_content(STRING_LONG_MARKDOWN)
    webhook.add_component(text_display)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


@pytest.mark.xfail
def test_component_text_display_validate() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Text Display
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    text_display: TextDisplay = TextDisplay(content=STRING_WORD)

    text_display.set_content(STRING_EXTRA_LONG)
    webhook.add_component(text_display)

    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to too many characters
    assert isinstance(res, Response) and res.ok


def test_component_thumbnail() -> None:
    """A test-case to validate the creation and execution of a Webhook with a Thumbnail Component."""

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    thumbnail: Thumbnail = Thumbnail(media=UnfurledMediaItem(url=STRING_URL_ICON_4))
    section: Section = Section(
        components=[], accessory=LinkButton(label=STRING_WORD, url=STRING_URL_GITHUB)
    )

    thumbnail.set_media(STRING_URL_ICON_1)
    thumbnail.set_description(STRING_SHORT)
    thumbnail.set_spoiler(True)
    section.add_component(TextDisplay(content=STRING_SHORT))
    section.add_component(TextDisplay(content=STRING_MEDIUM))
    section.add_component(TextDisplay(content=STRING_SHORT))
    section.set_accessory(thumbnail)
    webhook.add_component(section)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_unfurled_media_item() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with an Unfurled Media
    Item Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    gallery: MediaGallery = MediaGallery(items=[])
    frame: MediaGalleryItem = MediaGalleryItem(
        media=UnfurledMediaItem(url=STRING_URL_ICON_2)
    )
    picture: UnfurledMediaItem = UnfurledMediaItem()

    picture.set_url(STRING_URL_IMAGE_3)
    frame.set_media(picture)
    gallery.add_item(frame)
    webhook.add_component(gallery)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_component_mutator_branches() -> None:
    """Validate every Component collection and optional-field mutation."""
    buttons: list[LinkButton] = [
        LinkButton(label=f"Link {index}", url=STRING_URL_GITHUB) for index in range(5)
    ]
    action_row: ActionRow = ActionRow(components=buttons[:3])
    assert action_row.add_component(buttons[3:]) is action_row
    assert action_row.remove_component(buttons[0]) is action_row
    assert action_row.remove_component(0) is action_row
    assert action_row.remove_component([buttons[2], buttons[4]]) is action_row
    assert buttons[3].set_style(ButtonStyles.LINK) is buttons[3]

    container_text: list[ContainerComponent] = [
        TextDisplay(content=f"Container {index}") for index in range(5)
    ]
    container: Container = Container(
        components=container_text[:2], accent_color=STRING_COLOR_BLACK, spoiler=True
    )
    assert container.add_component(container_text[2:]) is container
    assert container.remove_component(container_text[0]) is container
    assert container.remove_component(0) is container
    assert (
        container.remove_component([container_text[2], container_text[4]]) is container
    )
    assert container.remove_accent_color() is container
    assert container.accent_color is UNSET
    assert container.set_accent_color(0x0E0E0E) is container
    assert container.remove_spoiler() is container
    assert container.spoiler is UNSET
    plain_container = Container(components=[TextDisplay(content="No accent color")])

    gallery_items: list[MediaGalleryItem] = [
        MediaGalleryItem(media=UnfurledMediaItem(url=url))
        for url in (
            STRING_URL_IMAGE_1,
            STRING_URL_IMAGE_2,
            STRING_URL_IMAGE_3,
            STRING_URL_IMAGE_4,
            STRING_URL_ICON_1,
        )
    ]
    first_item: MediaGalleryItem = gallery_items[0]
    assert first_item.set_media(STRING_URL_IMAGE_1) is first_item
    assert first_item.set_description(STRING_SHORT) is first_item
    assert first_item.remove_description() is first_item
    assert first_item.description is UNSET
    assert first_item.set_spoiler(True) is first_item
    assert first_item.remove_spoiler() is first_item
    assert first_item.spoiler is UNSET

    gallery: MediaGallery = MediaGallery(items=gallery_items[:3])
    assert gallery.add_item(gallery_items[3:]) is gallery
    assert gallery.remove_item(gallery_items[0]) is gallery
    assert gallery.remove_item(0) is gallery
    assert gallery.remove_item([gallery_items[2], gallery_items[4]]) is gallery

    section_text: list[TextDisplay] = [
        TextDisplay(content=f"Section {index}") for index in range(3)
    ]
    thumbnail_media = UnfurledMediaItem(url=STRING_URL_ICON_2)
    thumbnail: Thumbnail = Thumbnail(
        media=UnfurledMediaItem(url=STRING_URL_ICON_1),
        description=STRING_SHORT,
        spoiler=True,
    )
    assert thumbnail.set_media(thumbnail_media) is thumbnail
    assert thumbnail.media is thumbnail_media
    assert thumbnail.remove_description() is thumbnail
    assert thumbnail.description is UNSET
    assert thumbnail.remove_spoiler() is thumbnail
    assert thumbnail.spoiler is UNSET

    section: Section = Section(components=section_text[:1], accessory=thumbnail)
    assert section.add_component(section_text[1:]) is section
    assert section.remove_component(0) is section
    assert section.remove_component([section_text[1]]) is section

    seperator: Seperator = Seperator(divider=True, spacing=SeperatorSpacing.LARGE)
    assert seperator.remove_divider() is seperator
    assert seperator.divider is UNSET
    assert seperator.remove_spacing() is seperator
    assert seperator.spacing is UNSET

    file_media = UnfurledMediaItem(url="attachment://component.txt")
    file: File = File(file=UnfurledMediaItem(url="attachment://old.txt"))
    assert file.set_file("attachment://intermediate.txt") is file
    assert file.set_file(file_media) is file
    assert file.file is file_media
    assert file.set_spoiler(True) is file
    assert file.remove_spoiler() is file
    assert file.spoiler is UNSET

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    webhook.add_attachment("component.txt", b"Component attachment")
    webhook.add_component(
        [action_row, container, plain_container, gallery, section, seperator, file]
    )
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok
