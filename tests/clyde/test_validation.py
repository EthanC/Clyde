from datetime import UTC, datetime
from time import sleep
from typing import Annotated

import pytest
from msgspec import Meta, Struct
from niquests import Response

from clyde import EmbedFooter, Webhook
from clyde.poll import Poll
from clyde.validation import Validation

from .constants import FLOAT_TEST_DELAY, STRING_URL_GITHUB, STRING_URL_WEBHOOK


class NonStringUnion(Struct):
    """Provide a union field without a string member."""

    value: int | None


class DirectString(Struct):
    """Provide a directly constrained string field."""

    value: Annotated[str, Meta(max_length=12)]


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def test_validation_branches() -> None:
    """Validate conversions and type inspection before a live request."""
    assert Validation.convert_color(0xABCDEF) == 0xABCDEF
    assert Validation.convert_timestamp(1) == datetime.fromtimestamp(1.0).isoformat()
    assert Validation.convert_timestamp(1.5) == datetime.fromtimestamp(1.5).isoformat()
    direct = datetime(2000, 1, 1, tzinfo=UTC)
    assert Validation.convert_timestamp(direct) == direct.isoformat()

    assert (
        Validation.validate_url_scheme(STRING_URL_GITHUB, ["https"])
        == STRING_URL_GITHUB
    )
    with pytest.raises(ValueError, match="Empty URL"):
        Validation.validate_url_scheme(None, ["https", "attachment"])

    assert Validation.get_max_length(str, "value") is None
    assert Validation.get_max_length(EmbedFooter, "missing") is None
    assert Validation.get_max_length(DirectString, "value") == 12
    assert Validation.get_max_length(Poll, "duration") is None
    assert Validation.get_max_length(NonStringUnion, "value") is None

    res: Response = Webhook(
        url=STRING_URL_WEBHOOK, content="Validation branches passed"
    ).execute()

    assert isinstance(res, Response) and res.ok
