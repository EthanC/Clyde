from pathlib import Path
from time import sleep

import pytest
from httpx import Response

from clyde import (
    AllowedMentions,
    AllowedMentionTypes,
    Attachment,
    Markdown,
    Timestamp,
    Webhook,
)
from clyde.webhook import MessageFlags

from .constants import (
    FLOAT_TEST_DELAY,
    INT_TIMESTAMP,
    STRING_EMPTY,
    STRING_EXTRA_LONG,
    STRING_EXTRA_SHORT,
    STRING_ID_ROLE,
    STRING_ID_THREAD,
    STRING_ID_USER,
    STRING_LIST_MEDIUM,
    STRING_LIST_SHORT,
    STRING_LONG,
    STRING_LONG_MARKDOWN,
    STRING_MEDIUM,
    STRING_SHORT,
    STRING_URL_GITHUB,
    STRING_URL_ICON_1,
    STRING_URL_WEBHOOK,
)


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def test_webhook() -> None:
    """
    A test case to validate the creation of an empty Webhook instance.
    """

    assert Webhook(url=STRING_URL_WEBHOOK)


def test_webhook_execute() -> None:
    """
    A test-case to validate the successful execution of a minimal Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_execute_ratelimit() -> None:
    """
    A test-case to validate the successful execution of a Webhook instance which
    purposefully gets itself rate-limited.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    res: Response = webhook.execute()

    for _ in range(10):
        webhook.execute()

    assert isinstance(res, Response) and res.is_success


@pytest.mark.xfail
def test_webhook_execute_fail() -> None:
    """
    A test-case to validate the failure to execute a minimal Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_EMPTY)

    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to empty string
    assert isinstance(res, Response) and res.is_success


def test_webhook_set_content() -> None:
    """
    A test-case to validate the successful use and execution of set_content on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_LONG)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


@pytest.mark.xfail
def test_webhook_set_content_fail() -> None:
    """
    A test-case to validate the failure to execute a Webhook instance with content
    which exceeds the length limit.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_EXTRA_LONG)

    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to string length
    assert isinstance(res, Response) and res.is_success


def test_webhook_set_content_fallback() -> None:
    """
    A test-case to validate the successful use and execution of set_content with
    the fallback argument set to True on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_EXTRA_LONG, fallback=True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_username() -> None:
    """
    A test-case to validate the successful use and execution of set_username on
    a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_username(STRING_EXTRA_SHORT)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_avatar_url() -> None:
    """
    A test-case to validate the successful use and execution of set_avatar_url
    on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_avatar_url(STRING_URL_ICON_1)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_tts() -> None:
    """
    A test-case to validate the successful use and execution of set_tts on a Webhook
    instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)

    webhook.set_tts(True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_allowed_mentions() -> None:
    """
    A test-case to validate the successful use and execution of set_allowed_mentions
    on a Webhook instance.
    """
    webhook: Webhook = Webhook(
        url=STRING_URL_WEBHOOK, content=f"<@{STRING_ID_USER}> " + STRING_SHORT
    )
    mentions: AllowedMentions = AllowedMentions()

    mentions.add_parse(AllowedMentionTypes.USER_MENTIONS)
    mentions.add_user(STRING_ID_USER)
    mentions.add_parse(AllowedMentionTypes.ROLE_MENTIONS)
    mentions.add_role(STRING_ID_ROLE)
    mentions.remove_parse(AllowedMentionTypes.ROLE_MENTIONS)
    mentions.remove_role(STRING_ID_ROLE)

    webhook.set_allowed_mentions(mentions)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_plaintext() -> None:
    """
    A test-case to validate the successful use and execution of a plaintext bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/file_plaintext.txt", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_image() -> None:
    """
    A test-case to validate the successful use and execution of an image bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/image_1.png", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_image_multiple() -> None:
    """
    A test-case to validate the successful use and execution of multiple image
    bytes objects provided for Attachments on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    for i in range(4):
        with open(f"tests/clyde/data/image_{i + 1}.png", "rb") as handle:
            webhook.add_attachment(handle.name, handle.read(), spoiler=(i == 1))

    rnd: Attachment = webhook._attachments[2]
    rnd.set_spoiler(True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_binary() -> None:
    """
    A test-case to validate the successful use and execution of a binary bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/file_binary.bin", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_binary_multiple() -> None:
    """
    A test-case to validate the successful use and execution of multiple binary
    bytes objects provided for Attachments on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    for i in range(4):
        with open("tests/clyde/data/file_binary.bin", "rb") as handle:
            webhook.add_attachment(
                f"{handle.name}_{i}", handle.read(), spoiler=(i == 1)
            )

    rnd: Attachment = webhook._attachments[-1]
    rnd.set_filename("new_file.bin")
    rnd.set_spoiler(False)

    if isinstance(rnd.content, bytes):
        rnd.set_content(rnd.content * 2)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


@pytest.mark.xfail
def test_webhook_add_attachment_limit() -> None:
    """
    A test-case to validate the failure to execute a Webhook instance with too
    many file Attachments.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    for i in range(11):
        webhook.add_attachment(f"{i}.txt", str(i).encode())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_path() -> None:
    """
    A test-case to validate the successful use and execution of a Path object provided
    for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    file_path: Path = Path("tests/clyde/data/icon_3.png")

    webhook.add_attachment(file_path.name, file_path)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_add_attachment_path_multiple() -> None:
    """
    A test-case to validate the successful use and execution of multiple Path objects
    provided for Attachments on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    for file_path in Path("tests/clyde/data/").glob("image_*"):
        webhook.add_attachment(file_path.name, file_path)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_wait() -> None:
    """
    A test-case to validate the successful use and execution of set_wait on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_wait(True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_thread_id() -> None:
    """
    A test-case to validate the successful use and execution of set_thread_id on
    a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_thread_id(STRING_ID_THREAD)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_flag() -> None:
    """
    A test-case to validate the successful use and execution of set_flag on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(
        url=STRING_URL_WEBHOOK, content=f"<@{STRING_ID_USER}> " + STRING_SHORT
    )

    webhook.set_flag(MessageFlags.SUPPRESS_NOTIFICATIONS, True)
    webhook.set_flag(MessageFlags.SUPPRESS_EMBEDS, True)
    webhook.set_flag(MessageFlags.IS_COMPONENTS_V2, None)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_get_flag() -> None:
    """
    A test-case to validate the successful use and execution of get_flag on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_flag(MessageFlags.SUPPRESS_EMBEDS, True)

    assert webhook.get_flag(MessageFlags.SUPPRESS_EMBEDS)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_set_thread_name() -> None:
    """
    A test-case to validate the successful use of set_thread_name on a Webhook
    instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_thread_name(STRING_EXTRA_SHORT)

    # Do not attempt execution as the Tests Webhook URL is not a valid channel
    assert webhook.thread_name


def test_webhook_markdown() -> None:
    """
    A test-case to validate the successful execution of a Webhook instance
    with markdown formatting.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    content: str = ""

    content += Markdown.block_quote(STRING_MEDIUM, multi_line=False) + "\n"
    content += Markdown.bold(STRING_EXTRA_SHORT) + "\n"
    content += Markdown.bulleted_list(STRING_LIST_SHORT) + "\n"
    content += Markdown.code_block(STRING_LONG) + "\n"
    content += Markdown.header_1(STRING_EXTRA_SHORT) + "\n"
    content += Markdown.header_2(STRING_EXTRA_SHORT) + "\n"
    content += Markdown.header_3(STRING_EXTRA_SHORT) + "\n"
    content += Markdown.inline_code(STRING_SHORT) + "\n"
    content += Markdown.italics(STRING_SHORT) + "\n"
    content += Markdown.masked_link(STRING_EXTRA_SHORT, STRING_URL_GITHUB) + "\n"
    content += Markdown.numbered_list(STRING_LIST_MEDIUM) + "\n"
    content += Markdown.spoiler(STRING_MEDIUM) + "\n"
    content += Markdown.strikethrough(STRING_SHORT) + "\n"
    content += Markdown.subtext(STRING_MEDIUM) + "\n"
    content += Markdown.underline(STRING_SHORT) + "\n"
    content += Markdown.subtext(STRING_LONG_MARKDOWN) + "\n"

    webhook.set_content(content)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_webhook_timestamp() -> None:
    """
    A test-case to validate the successful execution of a Webhook instance
    with timestamp formatting.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    content: str = ""

    content += Timestamp.long_date(INT_TIMESTAMP) + "\n"
    content += Timestamp.long_date_time(INT_TIMESTAMP) + "\n"
    content += Timestamp.long_time(INT_TIMESTAMP) + "\n"
    content += Timestamp.relative_time(INT_TIMESTAMP) + "\n"
    content += Timestamp.short_date(INT_TIMESTAMP) + "\n"
    content += Timestamp.short_date_time(INT_TIMESTAMP) + "\n"
    content += Timestamp.short_time(INT_TIMESTAMP) + "\n"

    webhook.set_content(content=content)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success
