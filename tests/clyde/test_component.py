from time import sleep

import pytest
from httpx import Response

from clyde import Webhook
from clyde.components import (
    ActionRow,
    Container,
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
    action_row: ActionRow = ActionRow()

    action_row.add_component(
        LinkButton(label=STRING_EXTRA_SHORT, url=STRING_URL_GITHUB)
    )
    webhook.add_component(action_row)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_component_link_button() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Link Button
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    action_row: ActionRow = ActionRow()
    button: LinkButton = LinkButton()

    button.set_label(STRING_WORD)
    button.set_url(STRING_URL_DISCORD)
    action_row.add_component(button)
    webhook.add_component(action_row)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_component_container() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Container
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    container: Container = Container()
    body: TextDisplay = TextDisplay()

    body.set_content(STRING_LONG)
    container.set_spoiler(True)
    container.set_accent_color(STRING_COLOR_BLACK)
    container.add_component(body)
    webhook.add_component(container)

    container.add_component(TextDisplay(content=STRING_EXTRA_LONG))
    container.remove_component(-1)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_component_media_gallery() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Media Gallery
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    gallery: MediaGallery = MediaGallery()

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

    assert isinstance(res, Response) and res.is_success


def test_component_section() -> None:
    """A test-case to validate the creation and execution of a Webhook with a Section Component."""

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    section: Section = Section()

    section.add_component(TextDisplay(content=STRING_SHORT))
    section.add_component(TextDisplay(content=STRING_MEDIUM))

    bad_text: TextDisplay = TextDisplay(content=STRING_EXTRA_LONG)
    section.add_component(bad_text)
    section.remove_component(bad_text)

    section.add_component(TextDisplay(content=STRING_LONG))

    section.set_accessory(LinkButton(label=STRING_EXTRA_SHORT, url=STRING_URL_DISCORD))
    section.remove_accessory()
    section.set_accessory(LinkButton(label=STRING_EXTRA_SHORT, url=STRING_URL_GITHUB))

    webhook.add_component(section)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


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

    assert isinstance(res, Response) and res.is_success


def test_component_text_display() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Text Display
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    text_display: TextDisplay = TextDisplay()

    text_display.set_content(STRING_LONG_MARKDOWN)
    webhook.add_component(text_display)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


@pytest.mark.xfail
def test_component_text_display_validate() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with a Text Display
    Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    text_display: TextDisplay = TextDisplay()

    text_display.set_content(STRING_EXTRA_LONG)
    webhook.add_component(text_display)

    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to too many characters
    assert isinstance(res, Response) and res.is_success


def test_component_thumbnail() -> None:
    """A test-case to validate the creation and execution of a Webhook with a Thumbnail Component."""

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    thumbnail: Thumbnail = Thumbnail()
    section: Section = Section()

    thumbnail.set_media(STRING_URL_ICON_1)
    thumbnail.set_description(STRING_SHORT)
    thumbnail.set_spoiler(True)
    section.add_component(TextDisplay(content=STRING_SHORT))
    section.add_component(TextDisplay(content=STRING_MEDIUM))
    section.add_component(TextDisplay(content=STRING_SHORT))
    section.set_accessory(thumbnail)
    webhook.add_component(section)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_component_unfurled_media_item() -> None:
    """
    A test-case to validate the creation and execution of a Webhook with an Unfurled Media
    Item Component.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    gallery: MediaGallery = MediaGallery()
    frame: MediaGalleryItem = MediaGalleryItem()
    picture: UnfurledMediaItem = UnfurledMediaItem()

    picture.set_url(STRING_URL_IMAGE_3)
    frame.set_media(picture)
    gallery.add_item(frame)
    webhook.add_component(gallery)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success
