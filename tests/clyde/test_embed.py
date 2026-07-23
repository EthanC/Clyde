from copy import copy, deepcopy
from datetime import UTC, datetime
from time import sleep
from typing import Any, cast

import pytest
from msgspec import UNSET
from niquests import Response

from clyde import (
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
    EmbedImage,
    EmbedThumbnail,
    Webhook,
)

from .constants import (
    FLOAT_TEST_DELAY,
    FLOAT_TIMESTAMP,
    INT_TIMESTAMP,
    STRING_COLOR_WHITE,
    STRING_EXTRA_SHORT,
    STRING_LONG_MARKDOWN,
    STRING_SHORT,
    STRING_TIMESTAMP,
    STRING_URL_GITHUB,
    STRING_URL_ICON_1,
    STRING_URL_ICON_2,
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


def test_embed() -> None:
    """
    A test-case to validate the successful use and execution of an Embed on a
    Webhook object.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    embed: Embed = Embed()
    footer: EmbedFooter = EmbedFooter(text=STRING_SHORT)
    image: EmbedImage = EmbedImage(url=STRING_URL_ICON_1)
    thumbnail: EmbedThumbnail = EmbedThumbnail(url=STRING_URL_IMAGE_1)
    author: EmbedAuthor = EmbedAuthor(name=STRING_WORD)

    embed.set_title(STRING_SHORT)
    embed.set_description(STRING_LONG_MARKDOWN)
    embed.set_url(STRING_URL_GITHUB)
    embed.set_timestamp(INT_TIMESTAMP)
    embed.set_color(STRING_COLOR_WHITE)
    footer.set_text(STRING_EXTRA_SHORT)
    footer.set_icon_url(STRING_URL_ICON_4)
    embed.set_footer(footer)
    image.set_url(STRING_URL_IMAGE_4)
    embed.add_image(image)
    thumbnail.set_url(STRING_URL_ICON_2)
    embed.set_thumbnail(thumbnail)
    author.set_name(STRING_EXTRA_SHORT)
    author.set_url(STRING_URL_GITHUB)
    author.set_icon_url(STRING_URL_ICON_1)
    embed.set_author(author)
    embed.add_field(EmbedField(name="One", value="1", inline=True))
    embed.add_field(EmbedField(name="Two", value="2", inline=True))
    embed.add_field(EmbedField(name="Three", value="3", inline=True))
    embed.add_field(EmbedField(name="Four", value="4", inline=False))
    embed.add_field(EmbedField(name="Five", value="5", inline=False))
    embed.add_field(EmbedField(name="Six", value="6", inline=False))
    embed.add_field(EmbedField(name="Seven", value="7", inline=True))
    embed.add_field(EmbedField(name="Eight", value="8", inline=True))
    embed.add_field(EmbedField(name="Nine", value="9", inline=True))
    embed.add_field(EmbedField(name="Ten", value="10"))
    webhook.add_embed(embed)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_embed_image_gallery() -> None:
    """Validate transparent multi-image Embed galleries against Discord."""
    images: list[EmbedImage] = [
        EmbedImage(url=url)
        for url in (
            STRING_URL_IMAGE_1,
            STRING_URL_IMAGE_2,
            STRING_URL_IMAGE_3,
            STRING_URL_IMAGE_4,
        )
    ]
    gallery: Embed = Embed(title=STRING_SHORT)
    linked_gallery: Embed = Embed(description=STRING_EXTRA_SHORT, url=STRING_URL_GITHUB)

    assert gallery.add_image([]) is gallery
    assert gallery.add_image(images[0]) is gallery
    assert gallery.add_image(images[1:]) is gallery
    assert linked_gallery.add_image(images[:2]) is linked_gallery

    with pytest.raises(ValueError, match="more than 4 images"):
        gallery.add_image(EmbedImage(url=STRING_URL_ICON_1))

    copied_gallery: Embed = copy(gallery)
    copied_linked_gallery: Embed = deepcopy(linked_gallery)
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK).set_wait(True)
    webhook.add_embed([copied_gallery, copied_linked_gallery])
    res: Response = webhook.execute()
    response_embeds: list[dict[str, Any]] = res.json()["embeds"]

    assert isinstance(res, Response) and res.ok
    assert isinstance(webhook.embeds, list)
    assert len(webhook.embeds) == 2
    assert len(response_embeds) == 6
    assert [embed["url"] for embed in response_embeds[:4]] == [STRING_URL_IMAGE_1] * 4
    assert [embed["url"] for embed in response_embeds[4:]] == [STRING_URL_GITHUB] * 2
    assert [embed["image"]["url"] for embed in response_embeds] == [
        STRING_URL_IMAGE_1,
        STRING_URL_IMAGE_2,
        STRING_URL_IMAGE_3,
        STRING_URL_IMAGE_4,
        STRING_URL_IMAGE_1,
        STRING_URL_IMAGE_2,
    ]
    assert response_embeds[0]["title"] == STRING_SHORT
    assert all("title" not in embed for embed in response_embeds[1:])
    assert response_embeds[4]["description"] == STRING_EXTRA_SHORT
    assert "description" not in response_embeds[5]

    oversized: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    oversized.add_embed([Embed().add_image(images) for _ in range(3)])

    with pytest.raises(ValueError, match="more than 10 Embeds"):
        oversized.execute()

    assert gallery.remove_image() is gallery
    assert gallery.image is UNSET


def test_embed_timestamp_string() -> None:
    """
    A test-case to validate the successful use and execution of an Embed with an
    int object provided for the timestamp on a Webhook object.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    embed: Embed = Embed()

    embed.set_description(STRING_SHORT)
    embed.set_timestamp(STRING_TIMESTAMP)
    webhook.add_embed(embed)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_embed_timestamp_float() -> None:
    """
    A test-case to validate the successful use and execution of an Embed with a
    float object provided for the timestamp on a Webhook object.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    embed: Embed = Embed()

    embed.set_description(STRING_SHORT)
    embed.set_timestamp(FLOAT_TIMESTAMP)
    webhook.add_embed(embed)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_embed_timestamp_datetime() -> None:
    """
    A test-case to validate the successful use and execution of an Embed with a
    datetime object provided for the timestamp on a Webhook object.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    embed: Embed = Embed()

    embed.set_description(STRING_SHORT)
    embed.set_timestamp(datetime.now(UTC))
    webhook.add_embed(embed)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_embed_mutator_branches() -> None:
    """Validate optional removers and every Embed Field collection path."""
    author: EmbedAuthor = EmbedAuthor(
        name=STRING_WORD, url=STRING_URL_GITHUB, icon_url=STRING_URL_ICON_1
    )
    assert author.remove_url() is author
    assert author.url is UNSET
    assert author.remove_icon_url() is author
    assert author.icon_url is UNSET

    embed: Embed = Embed(
        title=STRING_SHORT,
        description=STRING_LONG_MARKDOWN,
        url=STRING_URL_GITHUB,
        timestamp=STRING_TIMESTAMP,
        color=STRING_COLOR_WHITE,
        footer=EmbedFooter(text=STRING_SHORT),
        image=EmbedImage(url=STRING_URL_IMAGE_1),
        thumbnail=EmbedThumbnail(url=STRING_URL_ICON_1),
        author=author,
    )
    for field_name, remover in (
        ("title", embed.remove_title),
        ("description", embed.remove_description),
        ("url", embed.remove_url),
        ("timestamp", embed.remove_timestamp),
        ("color", embed.remove_color),
        ("footer", embed.remove_footer),
        ("image", embed.remove_image),
        ("thumbnail", embed.remove_thumbnail),
        ("author", embed.remove_author),
    ):
        assert remover() is embed
        assert getattr(embed, field_name) is UNSET

    fields: list[EmbedField] = [
        EmbedField(name=f"Field {index}", value=str(index)) for index in range(3)
    ]
    assert embed.remove_field(fields[0]) is embed
    assert embed.add_field(fields) is embed
    assert embed.remove_field(fields[0]) is embed
    assert embed.remove_field(0) is embed
    assert embed.remove_field([fields[0]]) is embed
    assert embed.fields == [fields[2]]
    assert embed.remove_field([fields[2]]) is embed
    assert embed.fields is UNSET

    embed.set_description(STRING_SHORT).add_field(fields[0])
    res: Response = Webhook(url=STRING_URL_WEBHOOK).add_embed(embed).execute()

    assert isinstance(res, Response) and res.ok


def test_embed_validation_input_types() -> None:
    """Validate direct timestamp and color inputs through Discord serialization."""
    embeds: list[Embed] = [
        Embed(
            description="Integer", timestamp=cast(Any, INT_TIMESTAMP), color=0xFFFFFF
        ),
        Embed(description="Float", timestamp=cast(Any, FLOAT_TIMESTAMP)),
        Embed(description="Datetime", timestamp=cast(Any, datetime.now(UTC))),
    ]
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    assert webhook.add_embed(embeds) is webhook
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok
