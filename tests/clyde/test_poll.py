from time import sleep

import pytest
from httpx import Response

from clyde import Poll, PollAnswer, PollMediaAnswer, PollMediaQuestion, Webhook

from .constants import FLOAT_TEST_DELAY, STRING_MEDIUM, STRING_SHORT, STRING_URL_WEBHOOK


@pytest.fixture(autouse=True)
def delay() -> None:
    """Sleep between test-cases to prevent rate-limiting."""
    sleep(FLOAT_TEST_DELAY)


def test_poll() -> None:
    """
    A test-case to validate the successful execution of a Webhook with a Poll.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    webhook.set_poll(
        Poll(
            question=PollMediaQuestion(text=STRING_SHORT),
            answers=[
                PollAnswer(poll_media=PollMediaAnswer(text="A")),
                PollAnswer(poll_media=PollMediaAnswer(text="B")),
                PollAnswer(poll_media=PollMediaAnswer(text="C")),
                PollAnswer(poll_media=PollMediaAnswer(text="D")),
            ],
        )
    )
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


def test_poll_multiselect() -> None:
    """
    A test-case to validate the successful execution of a Webhook with a multi-select Poll.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    webhook.set_poll(
        Poll(
            question=PollMediaQuestion(text=STRING_MEDIUM),
            answers=[
                PollAnswer(poll_media=PollMediaAnswer(text="A")),
                PollAnswer(poll_media=PollMediaAnswer(text="B")),
                PollAnswer(poll_media=PollMediaAnswer(text="C")),
                PollAnswer(poll_media=PollMediaAnswer(text="D")),
            ],
            allow_multiselect=True,
        )
    )
    res: Response = webhook.execute()

    assert isinstance(res, Response) and res.is_success


@pytest.mark.xfail
def test_poll_answers_validate() -> None:
    """
    A test-case to validate the failure to execute a Webhook with a Poll that has too
    many answers.
    """

    webhook: Webhook = Webhook(url=STRING_URL_WEBHOOK)
    webhook.set_poll(
        Poll(
            question=PollMediaQuestion(text=STRING_SHORT),
            answers=[
                PollAnswer(poll_media=PollMediaAnswer(text="1")),
                PollAnswer(poll_media=PollMediaAnswer(text="2")),
                PollAnswer(poll_media=PollMediaAnswer(text="3")),
                PollAnswer(poll_media=PollMediaAnswer(text="4")),
                PollAnswer(poll_media=PollMediaAnswer(text="5")),
                PollAnswer(poll_media=PollMediaAnswer(text="6")),
                PollAnswer(poll_media=PollMediaAnswer(text="7")),
                PollAnswer(poll_media=PollMediaAnswer(text="8")),
                PollAnswer(poll_media=PollMediaAnswer(text="9")),
                PollAnswer(poll_media=PollMediaAnswer(text="10")),
                PollAnswer(poll_media=PollMediaAnswer(text="11")),
            ],
        )
    )
    res: Response = webhook.execute()

    # Webhook execution is expected to fail due to too many answers
    assert isinstance(res, Response) and res.is_success
