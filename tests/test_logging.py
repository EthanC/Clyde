import logging
from asyncio import run

import msgspec
import pytest
from niquests import HTTPError, RequestException, Response

from clyde import Attachment, Webhook


def _response(
    body: object | bytes,
    status_code: int,
    *,
    url: str = "https://discord.com/api/webhooks/1/test-token",
) -> Response:
    response = Response()
    response.status_code = status_code
    response.reason = "Bad Request" if status_code >= 400 else "OK"
    response.url = url
    response.encoding = "utf-8"
    response._content = body if isinstance(body, bytes) else msgspec.json.encode(body)

    return response


def _messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.name == "clyde.webhook"
    ]


def test_package_logger_has_null_handler() -> None:
    package_logger = logging.getLogger("clyde")

    assert any(
        isinstance(handler, logging.NullHandler) for handler in package_logger.handlers
    )


def test_content_fallback_logs_safe_sizes(caplog: pytest.LogCaptureFixture) -> None:
    content = "é" * 2001

    with caplog.at_level(logging.INFO, logger="clyde.webhook"):
        webhook = Webhook(url="https://discord.com/api/webhooks/1/test-token")
        webhook.set_content(content, fallback=True)

    messages = _messages(caplog)

    assert len(webhook._attachments) == 1
    assert any(
        message == "Added attachment fallback for oversized webhook content: "
        "characters=2,001, content_bytes=4,002, limit=2,000"
        for message in messages
    )
    assert content not in "\n".join(messages)


def test_request_build_logs_safe_metadata(caplog: pytest.LogCaptureFixture) -> None:
    query_secret = "QUERY_VALUE_SENTINEL"
    webhook = Webhook(
        url=(
            "https://discord.com/api/webhooks/1/test-token"
            f"?wait=True&private={query_secret}"
        ),
        content="Safe content",
    )
    webhook._query_params.update({"thread_id": "123", "private": query_secret})
    webhook._attachments.extend(
        [Attachment(content=b"missing name"), Attachment(filename="missing.bin")]
    )

    with caplog.at_level(logging.DEBUG, logger="clyde.webhook"):
        request = webhook._build_request(("content",), ("wait",))

    messages = _messages(caplog)

    assert "data" in request
    assert any(
        message
        == "Ignored unsupported webhook query parameters: url_count=1, stored_count=2"
        for message in messages
    )
    assert any(
        message
        == "Skipping incomplete webhook attachments: invalid_count=2, total_count=2, "
        "missing_filename_count=1, missing_content_count=1"
        for message in messages
    )
    assert any(
        message.startswith(
            "Built Discord webhook request: transport='json', edit=False, "
            "payload_fields=['content'], query_fields=['wait'], attachment_count=0, "
            "attachment_bytes=0"
        )
        for message in messages
    )
    assert query_secret not in "\n".join(messages)
    assert "missing.bin" not in "\n".join(messages)


def test_multipart_request_logs_attachment_totals(
    caplog: pytest.LogCaptureFixture,
) -> None:
    webhook = Webhook(
        url="https://discord.com/api/webhooks/1/test-token", content="Safe content"
    )
    webhook.add_attachment("private-name.bin", b"x" * 1234)

    with caplog.at_level(logging.DEBUG, logger="clyde.webhook"):
        request = webhook._build_request(("content",), ())

    messages = _messages(caplog)

    assert "files" in request
    assert any(
        "transport='multipart'" in message
        and "attachment_count=1" in message
        and "attachment_bytes=1,234" in message
        for message in messages
    )
    assert "private-name.bin" not in "\n".join(messages)


def test_http_error_redacts_url_token_and_payload_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    token = "WEBHOOK_TOKEN_SENTINEL_123456789"
    url = f"https://discord.com/api/webhooks/1/{token}"
    response = _response(
        {
            "message": f"Invalid token {token}",
            "code": 50035,
            "errors": {
                "content": {"_errors": [{"message": "Content must be a string"}]}
            },
        },
        400,
        url=url,
    )
    request = {"data": msgspec.json.encode({"content": 12345})}

    with (
        caplog.at_level(logging.DEBUG, logger="clyde.webhook"),
        pytest.raises(HTTPError) as caught,
    ):
        Webhook._raise_for_status(response, request)

    error_text = str(caught.value)
    messages = _messages(caplog)

    assert error_text.startswith(
        "Discord webhook request failed: status_code=400, reason='Bad Request'"
    )
    assert "<redacted>" in error_text
    assert token not in error_text
    assert url not in error_text
    assert any(
        message == "Discord rejected request field: path='content', value_type='int'"
        for message in messages
    )
    assert "12345" not in "\n".join(messages)
    assert token not in "\n".join(messages)


def test_http_error_handles_unknown_reason_without_url() -> None:
    response = _response(b"not json", 500, url="https://example.com/failure")
    response.reason = None
    response.url = None

    with pytest.raises(HTTPError) as caught:
        Webhook._raise_for_status(response)

    assert str(caught.value) == (
        "Discord webhook request failed: status_code=500, reason='Unknown'"
    )

    proxy_response = _response(
        b"not json", 502, url="https://webhook-proxy.example/failure"
    )

    with pytest.raises(HTTPError) as proxy_caught:
        Webhook._raise_for_status(proxy_response)

    assert "https://webhook-proxy.example" not in str(proxy_caught.value)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ({"retry_after": 0}, (0.0, "discord")),
        ({"retry_after": 1.25}, (1.25, "discord")),
        ({"retry_after": True}, (5.0, "default")),
        ({"retry_after": -1}, (5.0, "default")),
        (b'{"retry_after": NaN}', (5.0, "default")),
        ({"retry_after": "1.5"}, (5.0, "default")),
    ],
)
def test_ratelimit_delay_validation(
    body: object | bytes, expected: tuple[float, str]
) -> None:
    response = _response(body, 429)

    assert Webhook._ratelimit_retry(response) == expected


def test_ratelimit_delay_defaults_for_missing_or_invalid_json() -> None:
    missing = _response([], 429)
    malformed = _response(b"not json", 429)

    assert Webhook._ratelimit_retry(missing) == (5.0, "default")
    assert Webhook._ratelimit_retry(malformed) == (5.0, "default")


def test_sync_transport_failure_logs_type_only(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "SYNC_TRANSPORT_SECRET"

    with (
        caplog.at_level(logging.DEBUG, logger="clyde.webhook"),
        pytest.raises(RequestException) as caught,
    ):
        Webhook(url=f"http://127.0.0.1:1/webhooks/{secret}", content="Safe").execute()

    records = [record for record in caplog.records if record.name == "clyde.webhook"]
    messages = [record.getMessage() for record in records]

    error_type = type(caught.value).__name__
    assert any(
        message.startswith("Discord webhook transport failed")
        and f"error_type='{error_type}'" in message
        for message in messages
    )
    assert secret not in "\n".join(messages)
    assert not any(record.levelno >= logging.ERROR for record in records)


def test_async_transport_failure_logs_type_only(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "ASYNC_TRANSPORT_SECRET"

    with (
        caplog.at_level(logging.DEBUG, logger="clyde.webhook"),
        pytest.raises(RequestException) as caught,
    ):
        run(
            Webhook(
                url=f"http://127.0.0.1:1/webhooks/{secret}", content="Safe"
            ).execute_async()
        )

    records = [record for record in caplog.records if record.name == "clyde.webhook"]
    messages = [record.getMessage() for record in records]

    error_type = type(caught.value).__name__
    assert any(
        message.startswith("Discord webhook transport failed")
        and f"error_type='{error_type}'" in message
        for message in messages
    )
    assert secret not in "\n".join(messages)
    assert not any(record.levelno >= logging.ERROR for record in records)
