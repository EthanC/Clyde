"""Define the Poll class and its associates."""

from enum import IntEnum
from typing import Annotated, Self

import msgspec
from msgspec import UNSET, Meta, Struct, UnsetType


class PollMediaQuestion(Struct, kw_only=True):
    """
    Represent a Poll Media object for a question.

    https://discord.com/developers/docs/resources/poll#poll-media-object-poll-media-object-structure

    Attributes:
        text (UnsetType | str): The text of the field.
    """

    text: UnsetType | Annotated[str, Meta(min_length=1, max_length=300)] = (
        msgspec.field(default=UNSET)
    )
    """The text of the field."""

    def set_text(self: Self, text: str) -> "PollMediaQuestion":
        """
        Set the text of the Poll Media.

        Arguments:
            text (str): The text of the field.

        Returns:
            self (PollMediaQuestion): The modified Poll Media instance.
        """
        self.text = text

        return self

    def remove_text(self: Self) -> "PollMediaQuestion":
        """
        Remove the text from the Poll Media.

        Returns:
            self (PollMediaQuestion): The modified Poll Media instance.
        """
        self.text = UNSET

        return self


class PollMediaAnswer(Struct, kw_only=True):
    """
    Represent a Poll Media object for an answer.

    https://discord.com/developers/docs/resources/poll#poll-media-object-poll-media-object-structure

    Attributes:
        text (UnsetType | str): The text of the field.

        emoji (UnsetType | str): The emoji of the field.
    """

    text: UnsetType | Annotated[str, Meta(min_length=1, max_length=55)] = msgspec.field(
        default=UNSET
    )
    """The text of the field."""

    emoji: UnsetType | str = msgspec.field(default=UNSET)
    """The emoji of the field."""

    def set_text(self: Self, text: str) -> "PollMediaAnswer":
        """
        Set the text of the Poll Media.

        Arguments:
            text (str): The text of the field.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.text = text

        return self

    def remove_text(self: Self) -> "PollMediaAnswer":
        """
        Remove the text from the Poll Media.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.text = UNSET

        return self

    def set_emoji(self: Self, emoji: str) -> "PollMediaAnswer":
        """
        Set the emoji of the Poll Media.

        Arguments:
            emoji (str): The emoji of the field.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.emoji = emoji

        return self

    def remove_emoji(self: Self) -> "PollMediaAnswer":
        """
        Remove the emoji from the Poll Media.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.emoji = UNSET

        return self


class PollAnswer(Struct, kw_only=True):
    """
    Represent a Poll Answer object.

    https://discord.com/developers/docs/resources/poll#poll-answer-object-poll-answer-object-structure

    Attributes:
        poll_media (PollMediaAnswer): The data of the answer.
    """

    poll_media: PollMediaAnswer = msgspec.field()
    """The data of the answer."""

    def set_poll_media(self: Self, poll_media: PollMediaAnswer) -> "PollAnswer":
        """
        Set the media of the Poll Answer.

        Arguments:
            poll_media (PollMediaAnswer): The data of the answer.

        Returns:
            self (PollAnswer): The modified Poll Answer instance.
        """
        self.poll_media = poll_media

        return self


class LayoutType(IntEnum):
    """
    Define the available types of layouts for a Discord Poll.

    https://discord.com/developers/docs/resources/poll#layout-type

    Attributes:
        DEFAULT (int): The default layout type.
    """

    DEFAULT = 1
    """The default layout type."""


class Poll(Struct, kw_only=True):
    """
    Represent a Discord Poll object.

    https://discord.com/developers/docs/resources/poll#poll-create-request-object-poll-create-request-object-structure

    Attributes:
        question (PollMediaQuestion): The question of the poll.

        answers (list[PollAnswer]): Each of the answers available in the poll.

        duration (UnsetType | int): Number of hours the poll should be open for, up to
            32 days. Defaults to 24.

        allow_multiselect (UnsetType | bool): Whether a user can select multiple answers.

        layout_type (UnsetType | LayoutType): The layout type of the poll. Defaults
            to LayoutType.DEFAULT.
    """

    question: PollMediaQuestion = msgspec.field()
    """The question of the poll."""

    answers: Annotated[list[PollAnswer], Meta(min_length=1, max_length=10)] = (
        msgspec.field()
    )
    """Each of the answers available in the poll."""

    duration: UnsetType | int = msgspec.field(default=UNSET)
    """Number of hours the poll should be open for, up to 32 days. Defaults to 24."""

    allow_multiselect: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether a user can select multiple answers."""

    layout_type: UnsetType | LayoutType = msgspec.field(default=UNSET)
    """The layout type of the poll. Defaults to LayoutType.DEFAULT."""

    def set_question(self: Self, question: PollMediaQuestion) -> "Poll":
        """
        Set the question of the Poll.

        Arguments:
            question (PollMediaQuestion): The question of the poll.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.question = question

        return self

    def add_answer(self: Self, answer: PollAnswer | list[PollAnswer]) -> "Poll":
        """
        Add an answer to the Poll.

        Arguments:
            answer (PollAnswer | list[PollAnswer]): The Poll Answer or list of Poll Answers
                to add to the Poll.

        Returns:
            self (Poll): The modified Poll instance.
        """
        if not self.answers:
            self.answers = []

        if isinstance(answer, list):
            self.answers.extend(answer)
        else:
            self.answers.append(answer)

        return self

    def remove_answer(self: Self, answer: PollAnswer | list[PollAnswer]) -> "Poll":
        """
        Remove one or more answers from the Poll.

        Arguments:
            answer (PollAnswer | list[PollAnswer]): An answer or list of answers to
                remove.

        Returns:
            self (Poll): The modified Poll instance.
        """
        if isinstance(answer, PollAnswer):
            self.answers.remove(answer)
        else:
            self.answers = [entry for entry in self.answers if entry not in answer]

        return self

    def set_duration(self: Self, duration: int) -> "Poll":
        """
        Set the number of hours the Poll should be open for.

        Arguments:
            duration (int): Number of hours, up to 32 days.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.duration = duration

        return self

    def remove_duration(self: Self) -> "Poll":
        """
        Remove the number of hours the Poll should be open for.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.duration = UNSET

        return self

    def set_allow_multiselect(self: Self, allow_multiselect: bool) -> "Poll":
        """
        Set whether a user can select multiple answers on the Poll.

        Arguments:
            allow_multiselect (bool): Whether the user can select multiple answers.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.allow_multiselect = allow_multiselect

        return self

    def remove_allow_multiselect(self: Self) -> "Poll":
        """
        Remove whether a user can select multiple answers on the Poll.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.allow_multiselect = UNSET

        return self
