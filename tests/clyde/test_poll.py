from time import sleep

import pytest
from msgspec import UNSET
from niquests import Response

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

    assert isinstance(res, Response) and res.ok


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

    assert isinstance(res, Response) and res.ok


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
    assert isinstance(res, Response) and res.ok


def test_poll_mutator_branches() -> None:
    """Validate every Poll mutator before sending the result to Discord."""
    question: PollMediaQuestion = PollMediaQuestion(text="Original question")
    assert question.remove_text() is question
    assert question.text is UNSET
    assert question.set_text("Updated question") is question

    media: PollMediaAnswer = PollMediaAnswer(text="Original answer")
    assert media.remove_text() is media
    assert media.text is UNSET
    assert media.set_text("Updated answer") is media
    assert media.set_emoji("wave") is media
    assert media.remove_emoji() is media
    assert media.emoji is UNSET

    answers: list[PollAnswer] = [
        PollAnswer(poll_media=PollMediaAnswer(text=label))
        for label in ("A", "B", "C", "D")
    ]
    assert answers[0].set_poll_media(media) is answers[0]

    poll: Poll = Poll(question=PollMediaQuestion(text="Old"), answers=answers[:3])
    assert poll.set_question(question) is poll
    assert poll.remove_answer(answers[0]) is poll
    assert poll.remove_answer([answers[1]]) is poll
    assert poll.add_answer([answers[0], answers[1]]) is poll
    assert poll.add_answer(answers[3]) is poll
    assert poll.set_duration(48) is poll
    assert poll.remove_duration() is poll
    assert poll.duration is UNSET
    assert poll.set_allow_multiselect(True) is poll
    assert poll.remove_allow_multiselect() is poll
    assert poll.allow_multiselect is UNSET

    res: Response = Webhook(url=STRING_URL_WEBHOOK).set_poll(poll).execute()

    assert isinstance(res, Response) and res.ok
