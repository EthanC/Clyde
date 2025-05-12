"""Define the Poll class and its associates."""

from datetime import datetime
from enum import IntEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field


class PollMediaQuestion(BaseModel):
    """
    Represent a Poll Media object for a question.

    https://discord.com/developers/docs/resources/poll#poll-media-object-poll-media-object-structure

    Attributes:
        text (str | None): The text of the field.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Poll class."""

    text: str | None = Field(default=None, max_length=300)
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


class PollMediaAnswer(BaseModel):
    """
    Represent a Poll Media object for an answer.

    https://discord.com/developers/docs/resources/poll#poll-media-object-poll-media-object-structure

    Attributes:
        text (str | None): The text of the field.

        emoji (str | None): The emoji of the field.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Poll class."""

    text: str | None = Field(default=None, max_length=55)
    """The text of the field."""

    emoji: str | None = Field(default=None)
    """The emoji of the field."""

    def set_text(self: Self, text: str | None) -> "PollMediaAnswer":
        """
        Set the text of the Poll Media.

        Arguments:
            text (str | None): The text of the field. If set to None, the text is cleared.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.text = text

        return self

    def set_emoji(self: Self, emoji: str | None) -> "PollMediaAnswer":
        """
        Set the emoji of the Poll Media.

        Arguments:
            emoji (str | None): The emoji of the field. If set to None, the emoji is cleared.

        Returns:
            self (PollMediaAnswer): The modified Poll Media instance.
        """
        self.emoji = emoji

        return self


class PollAnswer(BaseModel):
    """
    Represent a Poll Answer object.

    https://discord.com/developers/docs/resources/poll#poll-answer-object-poll-answer-object-structure

    Attributes:
        poll_media (PollMediaAnswer): The data of the answer.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Poll class."""

    poll_media: PollMediaAnswer | None = None
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


class Poll(BaseModel):
    """
    Represent a Discord Poll object.

    https://discord.com/developers/docs/resources/poll#poll-create-request-object

    Attributes:
        question (PollMediaQuestion): The question of the poll.

        answers (list[PollAnswer]): Each of the answers available in the poll.

        expiry (int | float | datetime | None): The time when the poll ends.

        allow_multiselect (bool | None): Whether a user can select multiple answers.

        layout_type (LayoutType): The value of LayoutType.DEFAULT.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Poll class."""

    question: PollMediaQuestion | None = Field(default=None)
    """The question of the poll."""

    answers: list[PollAnswer] | None = Field(default=None, max_length=10)
    """Each of the answers available in the poll."""

    expiry: int | float | datetime | None = Field(default=None)
    """The time when the poll ends."""

    allow_multiselect: bool | None = Field(default=None)
    """Whether a user can select multiple answers."""

    layout_type: int = Field(default=LayoutType.DEFAULT, frozen=True)
    """The value of LayoutType.DEFAULT."""

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

    def remove_answer(
        self: Self, answer: PollAnswer | list[PollAnswer] | None
    ) -> "Poll":
        """
        Remove one or more answers from the Poll.

        Arguments:
            answer (PollAnswer | list[PollAnswer] | None): An answer or list of answers to
                remove. If set to None, all answers are removed.

        Returns:
            self (Poll): The modified Poll instance.
        """
        if self.answers:
            if not answer:
                self.answers = None
            elif isinstance(answer, list):
                for entry in answer:
                    self.answers.remove(entry)
            else:
                self.answers.remove(answer)

        return self

    def set_expiry(self: Self, expiry: int | float | datetime | None) -> "Poll":
        """
        Set the time when the Poll ends.

        Arguments:
            expiry (int | float | datetime | None): The time when the Poll ends. If set
                to None, the expiry is cleared.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.expiry = expiry

        return self

    def set_allow_multiselect(self: Self, allow_multiselect: bool | None) -> "Poll":
        """
        Set whether a user can select multiple answers on the Poll.

        Arguments:
            allow_multiselect (bool | None): Whether the user can select multiple answers.
                If set to None, allow_multiselect is cleared.

        Returns:
            self (Poll): The modified Poll instance.
        """
        self.allow_multiselect = allow_multiselect

        return self
