from time import sleep

import pytest
from httpx import Response

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
    INT_TIMESTAMP,
    STRING_COLOR_WHITE,
    STRING_EXTRA_SHORT,
    STRING_LONG_MARKDOWN,
    STRING_SHORT,
    STRING_URL_GITHUB,
    STRING_URL_ICON_1,
    STRING_URL_ICON_2,
    STRING_URL_ICON_4,
    STRING_URL_IMAGE_4,
    STRING_URL_WEBHOOK,
)


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def test_embed() -> None:
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    embed: Embed = Embed()
    footer: EmbedFooter = EmbedFooter()
    image: EmbedImage = EmbedImage()
    thumbnail: EmbedThumbnail = EmbedThumbnail()
    author: EmbedAuthor = EmbedAuthor()

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

    assert isinstance(res, Response) and res.is_success
