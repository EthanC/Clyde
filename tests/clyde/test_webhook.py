import logging
from asyncio import gather, run
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from time import sleep

import msgspec
import pytest
from niquests import HTTPError, PreparedRequest, Response

from clyde import (
    UNSET,
    AllowedMentions,
    AllowedMentionTypes,
    Attachment,
    Embed,
    Markdown,
    Message,
    Poll,
    PollAnswer,
    PollMediaAnswer,
    PollMediaQuestion,
    Timestamp,
    Webhook,
)
from clyde.components import TextDisplay
from clyde.webhook import MessageFlags

from .constants import (
    FLOAT_TEST_DELAY,
    FLOAT_TIMESTAMP,
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
    STRING_TIMESTAMP,
    STRING_URL_GITHUB,
    STRING_URL_ICON_1,
    STRING_URL_WEBHOOK,
)


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def _discord_response(body: object | bytes, status_code: int = 400) -> Response:
    """Build a Discord response without making a network request."""
    response = Response()
    response.status_code = status_code
    response.reason = "Bad Request" if status_code >= 400 else "OK"
    response.url = "https://discord.com/api/webhooks/1/token"
    response.encoding = "utf-8"
    response._content = body if isinstance(body, bytes) else msgspec.json.encode(body)

    return response


def test_webhook() -> None:
    """
    A test case to validate the creation of an empty Webhook instance.
    """

    assert Webhook(url=STRING_URL_WEBHOOK)


def test_webhook_http_error_includes_nested_discord_errors() -> None:
    """Resolve nested Discord error fields to readable payload paths."""
    response = _discord_response(
        {
            "message": "Invalid Form Body",
            "code": 50035,
            "errors": {
                "_errors": [
                    {
                        "code": "APPLICATION_COMMAND_TOO_LARGE",
                        "message": "Command exceeds maximum size (8000)",
                    },
                    {"message": "Request-level problem"},
                ],
                "embeds": {
                    "0": {
                        "fields": {
                            "6": {
                                "value": {
                                    "_errors": [
                                        {
                                            "code": "BASE_TYPE_MAX_LENGTH",
                                            "message": "Must be 1024 or fewer in length.",
                                        }
                                    ]
                                }
                            }
                        }
                    }
                },
                "components": {
                    "1": {
                        "components": {
                            "0": {
                                "_errors": [
                                    {
                                        "code": "UNION_TYPE_CHOICES",
                                        "message": 'Value of field "type" must be one of (1,).',
                                    },
                                    {"message": "Component-level problem"},
                                ]
                            }
                        }
                    }
                },
                "0": {"_errors": [{"message": "Root array item problem"}]},
                "ignored": 7,
            },
        }
    )
    request = PreparedRequest()
    response.request = request

    with pytest.raises(HTTPError) as caught:
        Webhook._raise_for_status(response)

    error = str(caught.value)
    assert "Discord API error 50035: Invalid Form Body" in error
    assert (
        "[APPLICATION_COMMAND_TOO_LARGE]: Command exceeds maximum size (8000)" in error
    )
    assert "Request-level problem" in error
    assert (
        "embeds[0].fields[6].value[BASE_TYPE_MAX_LENGTH]: Must be 1024 or fewer in length."
        in error
    )
    assert (
        'components[1].components[0][UNION_TYPE_CHOICES]: Value of field "type" must be one of (1,).'
        in error
    )
    assert "components[1].components[0]: Component-level problem" in error
    assert "[0]: Root array item problem" in error
    assert caught.value.response is response
    assert caught.value.request is request


def test_webhook_http_error_includes_legacy_field_errors() -> None:
    """Resolve Discord's field-to-message-list error response format."""
    response = _discord_response(
        {"thread_id": ['Value "not-a-snowflake" is not snowflake.'], "empty": []}
    )

    with pytest.raises(HTTPError, match="thread_id") as caught:
        Webhook._raise_for_status(response)

    assert 'thread_id: Value "not-a-snowflake" is not snowflake.' in str(caught.value)


def test_webhook_http_error_includes_message_without_code() -> None:
    """Include a Discord error message when no numeric API code is present."""
    response = _discord_response({"message": "Unknown Error"})

    with pytest.raises(HTTPError, match="Discord API error: Unknown Error"):
        Webhook._raise_for_status(response)


def test_webhook_http_error_logs_json_payload_piece(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log only the JSON payload value referenced by Discord's error path."""
    response = _discord_response(
        {
            "message": "Invalid Form Body",
            "code": 50035,
            "errors": {
                "_errors": [
                    {"code": "REQUEST_ERROR", "message": "Request-level problem"}
                ],
                "embeds": {
                    "0": {
                        "fields": {
                            "0": {
                                "value": {
                                    "_errors": [
                                        {
                                            "code": "BASE_TYPE_MAX_LENGTH",
                                            "message": "Must be 1024 or fewer in length.",
                                        },
                                        {
                                            "code": "SECOND_ERROR",
                                            "message": "Another problem with this value.",
                                        },
                                    ]
                                }
                            }
                        }
                    }
                },
            },
        }
    )
    request = {
        "data": msgspec.json.encode(
            {"embeds": [{"fields": [{"value": "problematic value"}]}]}
        )
    }
    caplog.set_level(logging.DEBUG, logger="clyde.webhook")

    with pytest.raises(HTTPError):
        Webhook._raise_for_status(response, request)

    records = [
        record
        for record in caplog.records
        if record.name == "clyde.webhook"
        and record.getMessage().startswith("Discord rejected request field")
    ]
    assert len(records) == 1
    assert records[0].levelno == logging.DEBUG
    assert records[0].getMessage() == (
        "Discord rejected request field: path='embeds[0].fields[0].value', "
        "value_type='str', value_length=17"
    )
    assert "problematic value" not in caplog.text


def test_webhook_http_error_logs_multipart_payload_piece(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Resolve a referenced Component from multipart payload_json."""
    response = _discord_response(
        {
            "message": "Invalid Form Body",
            "code": 50035,
            "errors": {
                "components": {
                    "0": {
                        "components": {
                            "0": {
                                "_errors": [
                                    {
                                        "code": "UNION_TYPE_CHOICES",
                                        "message": "Invalid Component type.",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }
    )
    payload = {"components": [{"components": [{"type": 10, "content": "Bad"}]}]}
    request = {
        "files": {
            "payload_json": (None, msgspec.json.encode(payload)),
            "files[0]": ("test.txt", b"test"),
        }
    }
    caplog.set_level(logging.DEBUG, logger="clyde.webhook")

    with pytest.raises(HTTPError):
        Webhook._raise_for_status(response, request)

    assert any(
        record.levelno == logging.DEBUG
        and record.getMessage()
        == "Discord rejected request field: path='components[0].components[0]', "
        "value_type='dict', value_length=2"
        for record in caplog.records
    )
    assert "Bad" not in caplog.text


def test_webhook_http_error_logs_missing_payload_piece(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Mark referenced payload paths that cannot be resolved."""
    response = _discord_response(
        {
            "message": "Invalid Form Body",
            "code": 50035,
            "errors": {
                "embeds": {
                    "0": {
                        "fields": {
                            "0": {
                                "value": {
                                    "_errors": [
                                        {
                                            "code": "BASE_TYPE_REQUIRED",
                                            "message": "This field is required",
                                        }
                                    ]
                                }
                            },
                            "1": {
                                "value": {
                                    "_errors": [
                                        {
                                            "code": "BASE_TYPE_REQUIRED",
                                            "message": "This field is required",
                                        }
                                    ]
                                }
                            },
                        }
                    }
                }
            },
        }
    )
    request = {
        "data": msgspec.json.encode(
            {"embeds": [{"fields": [{"name": "Missing value"}]}]}
        )
    }
    caplog.set_level(logging.DEBUG, logger="clyde.webhook")

    with pytest.raises(HTTPError):
        Webhook._raise_for_status(response, request)

    messages = [record.getMessage() for record in caplog.records]
    assert (
        "Discord rejected request field: path='embeds[0].fields[0].value', "
        "value_present=False" in messages
    )
    assert (
        "Discord rejected request field: path='embeds[0].fields[1].value', "
        "value_present=False" in messages
    )


def test_webhook_http_error_skips_unavailable_request_payloads(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Skip payload logging when the outgoing JSON is unavailable or invalid."""
    response = _discord_response(
        {
            "message": "Invalid Form Body",
            "code": 50035,
            "errors": {
                "content": {
                    "_errors": [
                        {
                            "code": "BASE_TYPE_MAX_LENGTH",
                            "message": "Must be 2000 or fewer in length.",
                        }
                    ]
                }
            },
        }
    )
    caplog.set_level(logging.DEBUG, logger="clyde.webhook")

    for request in ({}, {"files": []}, {"files": {}}, {"data": b"not json"}):
        caplog.clear()

        with pytest.raises(HTTPError):
            Webhook._raise_for_status(response, request)

        assert not any(
            record.getMessage().startswith("Discord rejected request field")
            for record in caplog.records
        )


@pytest.mark.parametrize("body", [b"not json", [], {}])
def test_webhook_http_error_ignores_unresolved_bodies(body: object | bytes) -> None:
    """Retain the standard HTTP error when Discord provides no useful details."""
    response = _discord_response(body)
    expected = "Discord webhook request failed: status_code=400, reason='Bad Request'"

    with pytest.raises(HTTPError, match="status_code=400") as caught:
        Webhook._raise_for_status(response)

    assert str(caught.value) == expected


def test_webhook_raise_for_status_returns_success() -> None:
    """Return successful responses unchanged."""
    response = _discord_response({}, status_code=200)

    assert Webhook._raise_for_status(response) is response


def test_webhook_execute() -> None:
    """
    A test-case to validate the successful execution of a minimal Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_get() -> None:
    """Validate token-authenticated Webhook retrieval against Discord."""
    webhook = Webhook(url=f"{STRING_URL_WEBHOOK}/?wait=True#fragment")
    result = webhook.get()

    assert isinstance(result, Webhook)
    assert isinstance(result.id, str)
    assert result.type == 1
    assert isinstance(result.guild_id, str)
    assert isinstance(result.channel_id, str)
    assert isinstance(result.name, str)
    assert isinstance(result.url, str)

    async_result = run(webhook.get_async())

    assert async_result == result


def test_webhook_modify() -> None:
    """Validate token-authenticated Webhook modifications against Discord."""
    webhook = Webhook(url=f"{STRING_URL_WEBHOOK}/?wait=True#fragment")
    avatar_path = Path("tests/clyde/data/image_1.png")

    modified: Response = webhook.modify(
        name=STRING_EXTRA_SHORT, avatar=avatar_path, reason="Test webhook modification"
    )
    modified_data: dict = modified.json()

    assert isinstance(modified, Response) and modified.ok
    assert modified_data["name"] == STRING_EXTRA_SHORT
    assert modified_data["avatar"] is not None
    assert "user" not in modified_data

    modified_bytes: Response = run(
        webhook.modify_async(
            avatar=Path("tests/clyde/data/image_2.png").read_bytes(),
            reason="Test bytes avatar modification",
        )
    )
    modified_bytes_data: dict = modified_bytes.json()

    assert isinstance(modified_bytes, Response) and modified_bytes.ok
    assert modified_bytes_data["name"] == STRING_EXTRA_SHORT
    assert modified_bytes_data["avatar"] is not None
    assert modified_bytes_data["avatar"] != modified_data["avatar"]
    assert "user" not in modified_bytes_data

    cleared: Response = webhook.modify(avatar=None, reason="Clear test webhook avatar")
    cleared_data: dict = cleared.json()

    assert isinstance(cleared, Response) and cleared.ok
    assert cleared_data["name"] == STRING_EXTRA_SHORT
    assert cleared_data["avatar"] is None
    assert "user" not in cleared_data

    unchanged: Response = webhook.modify()

    assert isinstance(unchanged, Response) and unchanged.ok
    assert unchanged.json()["name"] == STRING_EXTRA_SHORT

    with pytest.raises(ValueError, match="PNG, JPEG, or GIF"):
        webhook.modify(avatar=b"not an image")


def test_webhook_delete_validation() -> None:
    """Validate DELETE audit-log reasons without sending a request."""
    webhook = Webhook(url=STRING_URL_WEBHOOK)

    assert Webhook._audit_log_request(None) == {}
    assert Webhook._audit_log_request("Cleanup / café?") == {
        "headers": {"X-Audit-Log-Reason": "Cleanup%20%2F%20caf%C3%A9%3F"}
    }

    with pytest.raises(ValueError, match="between 1 and 512"):
        webhook.delete(reason="")
    with pytest.raises(ValueError, match="between 1 and 512"):
        run(webhook.delete_async(reason="x" * 513))


def test_webhook_get_message() -> None:
    """Validate synchronous and asynchronous message retrieval against Discord."""
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT).set_wait(
        True
    )
    created: Response = webhook.execute()
    message_id: str = created.json()["id"]
    getter: Webhook = Webhook(url=f"{STRING_URL_WEBHOOK}/?wait=True#fragment")

    message: Message = getter.get_message(message_id)

    assert isinstance(message, Message)
    assert message.id == message_id
    assert message.content == STRING_SHORT
    assert isinstance(message.webhook_id, str)

    async_message: Message = run(getter.get_message_async(message_id))

    assert async_message == message


def test_webhook_edit_message() -> None:
    """Validate editing the content of an existing Webhook message."""
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    webhook.set_wait(True)
    created: Response = webhook.execute()
    message_id: str = created.json()["id"]

    editor: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_MEDIUM)
    edited: Response = editor.edit_message(message_id)
    edited_data: dict = edited.json()

    assert isinstance(edited, Response) and edited.ok
    assert edited_data["id"] == message_id
    assert edited_data["content"] == STRING_MEDIUM


def test_webhook_edit_message_async() -> None:
    """Validate asynchronously editing an existing Webhook message."""
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    webhook.set_wait(True)
    created: Response = webhook.execute()
    message_id: str = created.json()["id"]

    editor: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_MEDIUM)
    edited: Response = run(editor.edit_message_async(message_id))
    edited_data: dict = edited.json()

    assert isinstance(edited, Response) and edited.ok
    assert edited_data["id"] == message_id
    assert edited_data["content"] == STRING_MEDIUM


def test_webhook_edit_message_attachments() -> None:
    """Validate clearing fields and retaining, adding, and clearing Attachments."""
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    webhook.set_wait(True)
    webhook.add_embed(Embed(description=STRING_SHORT))
    webhook.add_attachment(
        "original.txt", b"original", description="Original attachment"
    )
    created: Response = webhook.execute()
    created_data: dict = created.json()
    message_id: str = created_data["id"]
    attachment_id: str = created_data["attachments"][0]["id"]

    assert created_data["attachments"][0]["description"] == "Original attachment"

    editor: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=None)
    editor.remove_embed(None)
    editor.retain_attachment(attachment_id, description="Retained attachment")
    editor.add_attachment("new.txt", b"new", description="New attachment")
    edited: Response = editor.edit_message(message_id)
    edited_data: dict = edited.json()
    edited_attachments: list[dict] = edited_data["attachments"]

    assert isinstance(edited, Response) and edited.ok
    assert edited_data["content"] == ""
    assert edited_data["embeds"] == []
    assert len(edited_attachments) == 2
    assert edited_attachments[0]["description"] == "Retained attachment"
    assert edited_attachments[1]["description"] == "New attachment"

    cleared: Response = (
        Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
        .clear_attachments()
        .edit_message(message_id)
    )

    assert isinstance(cleared, Response) and cleared.ok
    assert cleared.json()["attachments"] == []


def test_webhook_edit_message_components() -> None:
    """Validate converting a real Discord message to Components."""
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    webhook.set_wait(True)
    created: Response = webhook.execute()
    message_id: str = created.json()["id"]

    editor: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=None, embeds=None)
    editor.add_component(TextDisplay(content=STRING_MEDIUM))
    edited: Response = editor.edit_message(message_id)
    edited_data: dict = edited.json()

    assert isinstance(edited, Response) and edited.ok
    assert edited_data["id"] == message_id
    assert edited_data["content"] == ""
    assert edited_data["embeds"] == []
    assert edited_data["flags"] & MessageFlags.IS_COMPONENTS_V2
    assert len(edited_data["components"]) == 1
    assert edited_data["components"][0]["type"] == 10
    assert edited_data["components"][0]["content"] == STRING_MEDIUM


def test_webhook_execute_requires_message() -> None:
    """Reject execution without a message field before sending a request."""
    webhooks: list[Webhook] = [
        Webhook(url=STRING_URL_WEBHOOK),
        Webhook(url=STRING_URL_WEBHOOK, content=None, embeds=None, components=None),
        Webhook(url=STRING_URL_WEBHOOK, content=STRING_EMPTY, embeds=[], components=[]),
    ]
    error = "at least one of content, embeds, components, file, or poll"

    for webhook in webhooks:
        with pytest.raises(ValueError, match=error):
            webhook.execute()

    with pytest.raises(ValueError, match=error):
        run(Webhook(url=STRING_URL_WEBHOOK).execute_async())


def test_webhook_set_content() -> None:
    """
    A test-case to validate the successful use and execution of set_content on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_LONG)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


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
    assert isinstance(res, Response) and res.ok


def test_webhook_set_content_fallback() -> None:
    """
    A test-case to validate the successful use and execution of set_content with
    the fallback argument set to True on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    webhook.set_content(STRING_SHORT, fallback=True)
    webhook.set_content(STRING_EXTRA_LONG, fallback=True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_set_username() -> None:
    """
    A test-case to validate the successful use and execution of set_username on
    a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_username(STRING_EXTRA_SHORT)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_set_avatar_url() -> None:
    """
    A test-case to validate the successful use and execution of set_avatar_url
    on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_avatar_url(STRING_URL_ICON_1)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_set_tts() -> None:
    """
    A test-case to validate the successful use and execution of set_tts on a Webhook
    instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)

    webhook.set_tts(True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


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

    assert isinstance(res, Response) and res.ok


def test_webhook_add_attachment_plaintext() -> None:
    """
    A test-case to validate the successful use and execution of a plaintext bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/file_plaintext.txt", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_add_attachment_image() -> None:
    """
    A test-case to validate the successful use and execution of an image bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/image_1.png", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


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

    assert isinstance(res, Response) and res.ok


def test_webhook_add_attachment_binary() -> None:
    """
    A test-case to validate the successful use and execution of a binary bytes
    object provided for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    with open("tests/clyde/data/file_binary.bin", "rb") as handle:
        webhook.add_attachment(handle.name, handle.read())

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


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

    assert isinstance(res, Response) and res.ok


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

    assert isinstance(res, Response) and res.ok


def test_webhook_add_attachment_path() -> None:
    """
    A test-case to validate the successful use and execution of a Path object provided
    for an Attachment on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    file_path: Path = Path("tests/clyde/data/icon_3.png")

    webhook.add_attachment(file_path.name, file_path)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_add_attachment_path_multiple() -> None:
    """
    A test-case to validate the successful use and execution of multiple Path objects
    provided for Attachments on a Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)

    for file_path in Path("tests/clyde/data/").glob("image_*"):
        webhook.add_attachment(file_path.name, file_path)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_set_wait() -> None:
    """
    A test-case to validate the successful use and execution of set_wait on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_wait(True)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_set_thread_id() -> None:
    """
    A test-case to validate the successful use of set_thread_id on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_thread_id(STRING_ID_THREAD)

    assert webhook._query_params["thread_id"] == STRING_ID_THREAD

    webhook.set_thread_id(None)

    assert "thread_id" not in webhook._query_params


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

    assert isinstance(res, Response) and res.ok


def test_webhook_get_flag() -> None:
    """
    A test-case to validate the successful use and execution of get_flag on a
    Webhook instance.
    """
    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK, content=STRING_LONG)

    webhook.set_flag(MessageFlags.SUPPRESS_EMBEDS, True)

    assert webhook.get_flag(MessageFlags.SUPPRESS_EMBEDS)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


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

    content += Markdown.block_quote(STRING_SHORT) + "\n"
    content += Markdown.block_quote(STRING_MEDIUM, multi_line=False) + "\n"
    content += Markdown.bold(STRING_EXTRA_SHORT) + "\n"
    content += Markdown.bulleted_list(STRING_LIST_SHORT) + "\n"
    content += Markdown.code_block(STRING_LONG) + "\n"
    content += Markdown.code_block(STRING_SHORT, "python") + "\n"
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

    assert isinstance(res, Response) and res.ok


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
    content += Timestamp.short_time(FLOAT_TIMESTAMP) + "\n"
    content += Timestamp.short_time(STRING_TIMESTAMP) + "\n"
    content += (
        Timestamp.short_time(datetime.fromtimestamp(INT_TIMESTAMP, tz=UTC)) + "\n"
    )

    webhook.set_content(content=content)

    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok


def test_webhook_allowed_mentions_branches() -> None:
    """Validate Allowed Mentions mutations through a live Webhook request."""
    blocked_users = AllowedMentions(users=[STRING_ID_USER])
    assert blocked_users.add_parse(AllowedMentionTypes.USER_MENTIONS) is blocked_users
    assert blocked_users.parse is UNSET

    blocked_roles = AllowedMentions(roles=[STRING_ID_ROLE])
    assert blocked_roles.add_parse(AllowedMentionTypes.ROLE_MENTIONS) is blocked_roles
    assert blocked_roles.parse is UNSET

    mentions = AllowedMentions()
    assert mentions.remove_parse(AllowedMentionTypes.USER_MENTIONS) is mentions
    assert mentions.add_parse(list(AllowedMentionTypes)) is mentions
    assert mentions.remove_parse(AllowedMentionTypes.USER_MENTIONS) is mentions
    assert mentions.remove_parse(0) is mentions
    assert (
        mentions.add_parse(
            [AllowedMentionTypes.USER_MENTIONS, AllowedMentionTypes.ROLE_MENTIONS]
        )
        is mentions
    )
    assert (
        mentions.remove_parse(
            [AllowedMentionTypes.USER_MENTIONS, AllowedMentionTypes.ROLE_MENTIONS]
        )
        is mentions
    )
    assert mentions.remove_parse(AllowedMentionTypes.EVERYONE_MENTIONS) is mentions
    assert mentions.parse is UNSET

    role_blocked = AllowedMentions(parse=[AllowedMentionTypes.ROLE_MENTIONS])
    assert role_blocked.add_role(STRING_ID_ROLE) is role_blocked
    assert role_blocked.roles is UNSET
    assert mentions.remove_role(STRING_ID_ROLE) is mentions
    assert mentions.add_role([STRING_ID_ROLE]) is mentions
    assert mentions.add_role("0") is mentions
    assert mentions.remove_role(STRING_ID_ROLE) is mentions
    assert mentions.remove_role(0) is mentions
    assert mentions.add_role([STRING_ID_ROLE, "0"]) is mentions
    assert mentions.remove_role([STRING_ID_ROLE]) is mentions
    assert mentions.remove_role(["0"]) is mentions
    assert mentions.roles is UNSET

    user_blocked = AllowedMentions(parse=[AllowedMentionTypes.USER_MENTIONS])
    assert user_blocked.add_user(STRING_ID_USER) is user_blocked
    assert user_blocked.users is UNSET
    assert mentions.remove_user(STRING_ID_USER) is mentions
    assert mentions.add_user([STRING_ID_USER]) is mentions
    assert mentions.add_user("0") is mentions
    assert mentions.remove_user(STRING_ID_USER) is mentions
    assert mentions.remove_user(0) is mentions
    assert mentions.add_user([STRING_ID_USER, "0"]) is mentions
    assert mentions.remove_user([STRING_ID_USER]) is mentions
    assert mentions.remove_user(["0"]) is mentions
    assert mentions.users is UNSET
    assert mentions.set_replied_user(False) is mentions

    res: Response = (
        Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
        .set_allowed_mentions(mentions)
        .execute()
    )

    assert isinstance(res, Response) and res.ok


def test_webhook_collection_branches() -> None:
    """Validate Webhook Embed and Component collection operations live."""
    embeds = [Embed(description=f"Embed {index}") for index in range(5)]
    embed_webhook = Webhook(url=STRING_URL_WEBHOOK)
    assert embed_webhook.remove_embed(embeds[0]) is embed_webhook
    assert embed_webhook.add_embed(embeds[:3]) is embed_webhook
    assert embed_webhook.add_embed(embeds[3]) is embed_webhook
    assert embed_webhook.remove_embed(embeds[0]) is embed_webhook
    assert embed_webhook.remove_embed(0) is embed_webhook
    assert embed_webhook.remove_embed([embeds[2]]) is embed_webhook
    assert embed_webhook.remove_embed([embeds[3]]) is embed_webhook
    assert embed_webhook.embeds is UNSET
    embed_webhook.add_embed(embeds[4])
    embed_res: Response = embed_webhook.execute()

    components = [TextDisplay(content=f"Component {index}") for index in range(4)]
    component_webhook = Webhook(url=STRING_URL_WEBHOOK)
    assert component_webhook.remove_component(components[0]) is component_webhook
    assert component_webhook.add_component(components[:3]) is component_webhook
    assert component_webhook.add_component(components[3]) is component_webhook
    assert component_webhook.remove_component(components[0]) is component_webhook
    assert component_webhook.remove_component(0) is component_webhook
    assert component_webhook.remove_component([components[2]]) is component_webhook
    assert component_webhook.remove_component([components[3]]) is component_webhook
    assert component_webhook.components is UNSET
    assert component_webhook.remove_component(None) is component_webhook
    component_webhook.add_component(components[0])
    component_res: Response = component_webhook.execute()

    assert isinstance(embed_res, Response) and embed_res.ok
    assert isinstance(component_res, Response) and component_res.ok


def test_webhook_attachment_branches() -> None:
    """Validate Attachment mutations and filtering through Discord."""
    path_attachment = Attachment(filename="path.txt")
    assert (
        path_attachment.set_content(Path("tests/clyde/data/file_plaintext.txt"))
        is path_attachment
    )
    assert isinstance(path_attachment.content, bytes)
    with pytest.raises(ValueError, match="1,024 or fewer"):
        path_attachment.set_description("x" * 1025)

    unnamed = Attachment()
    assert unnamed.set_spoiler(True) is unnamed
    assert unnamed.filename is UNSET
    prefixed = Attachment(filename="SPOILER_report.txt", content=b"report")
    assert prefixed.set_spoiler(False) is prefixed
    assert prefixed.filename == "report.txt"

    attachments = [
        Attachment(filename=f"file-{index}.txt", content=str(index).encode())
        for index in range(5)
    ]
    webhook = Webhook(url=f"{STRING_URL_WEBHOOK}?wait=False")
    webhook._attachments.extend(attachments)
    assert webhook.remove_attachment(attachments[0]) is webhook
    assert webhook.remove_attachment(0) is webhook
    assert webhook.remove_attachment("file-2.txt") is webhook
    assert webhook.remove_attachment([attachments[3]]) is webhook
    webhook._attachments.append(Attachment())
    assert webhook.set_wait(None) is webhook
    assert "wait=" not in webhook.url
    webhook.set_wait(True)
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.ok
    assert res.json()["attachments"][0]["filename"] == "file-4.txt"


def test_webhook_edit_validation_branches() -> None:
    """Validate edit-only failures and perform a real attachment edit."""
    created: Response = (
        Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
        .set_wait(True)
        .add_attachment("original.txt", b"original")
        .execute()
    )
    created_data: dict = created.json()
    message_id: str = created_data["id"]
    attachment_id: str = created_data["attachments"][0]["id"]

    editor = Webhook(url=STRING_URL_WEBHOOK, content=STRING_MEDIUM)
    with pytest.raises(ValueError, match="attachment_id must not be empty"):
        editor.retain_attachment("")
    with pytest.raises(ValueError, match="1024 or fewer"):
        editor.retain_attachment(attachment_id, description="x" * 1025)
    with pytest.raises(ValueError, match="message_id must not be empty"):
        editor.edit_message("")

    invalid_flags = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    invalid_flags.set_flag(MessageFlags.SUPPRESS_NOTIFICATIONS, True)
    with pytest.raises(ValueError, match="only support SUPPRESS_EMBEDS"):
        invalid_flags.edit_message(message_id)

    missing_manifest = Webhook(url=STRING_URL_WEBHOOK, content=STRING_SHORT)
    missing_manifest.add_attachment("new.txt", b"new")
    with pytest.raises(ValueError, match=r"Call retain_attachment\(\)"):
        missing_manifest.edit_message(message_id)

    invalid_components = Webhook(
        url=STRING_URL_WEBHOOK,
        content=STRING_SHORT,
        embeds=[Embed(description=STRING_SHORT)],
        poll=Poll(
            question=PollMediaQuestion(text="Question"),
            answers=[PollAnswer(poll_media=PollMediaAnswer(text="Answer"))],
        ),
    )
    invalid_components.add_attachment("component.txt", b"Component attachment")
    invalid_components.add_component(TextDisplay(content=STRING_SHORT))
    with pytest.raises(ValueError, match=r"non-null content, embeds, files\[n\], poll"):
        invalid_components.execute()

    assert editor.retain_attachment(attachment_id, description="First") is editor
    assert editor.retain_attachment(attachment_id, description="Updated") is editor
    editor.add_attachment("new.txt", b"new")
    editor.set_flag(MessageFlags.SUPPRESS_EMBEDS, True)
    edited: Response = editor.edit_message(message_id)

    assert isinstance(edited, Response) and edited.ok
    assert len(edited.json()["attachments"]) == 2


def test_webhook_sync_ratelimit(caplog: pytest.LogCaptureFixture) -> None:
    """Log and recover from a live synchronous Discord rate limit."""
    caplog.set_level(logging.DEBUG, logger="clyde.webhook")
    responses: list[Response] = []

    for _ in range(3):
        caplog.clear()

        with ThreadPoolExecutor(max_workers=8) as executor:
            responses = list(
                executor.map(
                    lambda index: Webhook(
                        url=STRING_URL_WEBHOOK, content=f"Sync rate limit {index}"
                    ).execute(),
                    range(8),
                )
            )

        records = [
            record for record in caplog.records if record.name == "clyde.webhook"
        ]

        if any(
            record.getMessage().startswith("Discord rate limit received; retrying")
            for record in records
        ):
            break

    records = [record for record in caplog.records if record.name == "clyde.webhook"]
    messages = [record.getMessage() for record in records]

    assert responses and all(response.ok for response in responses)
    assert any(
        record.levelno == logging.WARNING
        and record.getMessage().startswith("Discord rate limit received; retrying")
        for record in records
    )
    assert any(
        record.levelno == logging.INFO
        and record.getMessage().startswith(
            "Discord webhook request recovered after rate limiting"
        )
        for record in records
    )
    assert not any(record.levelno >= logging.ERROR for record in records)
    assert STRING_URL_WEBHOOK not in "\n".join(messages)


def test_webhook_async_ratelimit(caplog: pytest.LogCaptureFixture) -> None:
    """Log and recover from a live asynchronous Discord rate limit."""

    async def execute_batch() -> list[Response]:
        return await gather(
            *[
                Webhook(
                    url=STRING_URL_WEBHOOK, content=f"Async rate limit {index}"
                ).execute_async()
                for index in range(8)
            ]
        )

    caplog.set_level(logging.DEBUG, logger="clyde.webhook")
    responses: list[Response] = []

    for _ in range(3):
        caplog.clear()
        responses = run(execute_batch())
        records = [
            record for record in caplog.records if record.name == "clyde.webhook"
        ]

        if any(
            record.getMessage().startswith("Discord rate limit received; retrying")
            for record in records
        ):
            break

    records = [record for record in caplog.records if record.name == "clyde.webhook"]
    messages = [record.getMessage() for record in records]

    assert responses and all(response.ok for response in responses)
    assert any(
        record.levelno == logging.WARNING
        and record.getMessage().startswith("Discord rate limit received; retrying")
        for record in records
    )
    assert any(
        record.levelno == logging.INFO
        and record.getMessage().startswith(
            "Discord webhook request recovered after rate limiting"
        )
        for record in records
    )
    assert not any(record.levelno >= logging.ERROR for record in records)
    assert STRING_URL_WEBHOOK not in "\n".join(messages)
