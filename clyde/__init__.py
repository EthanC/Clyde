"""
A modern, type-hinted Python library for seamless interaction with the Discord Webhook API.

https://github.com/EthanC/Clyde
"""

import logging

from msgspec import UNSET, UnsetType

logging.getLogger(__name__).addHandler(logging.NullHandler())

from clyde.attachment import Attachment
from clyde.component import Component
from clyde.embed import (
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
    EmbedImage,
    EmbedThumbnail,
)
from clyde.markdown import Markdown
from clyde.message import Message
from clyde.poll import Poll, PollAnswer, PollMediaAnswer, PollMediaQuestion
from clyde.timestamp import Timestamp, TimestampStyles
from clyde.webhook import (
    AllowedMentions,
    AllowedMentionTypes,
    TopLevelComponent,
    Webhook,
)

__all__: list[str] = [
    "UNSET",
    "UnsetType",
    "Attachment",
    "Component",
    "Embed",
    "EmbedAuthor",
    "EmbedField",
    "EmbedFooter",
    "EmbedImage",
    "EmbedThumbnail",
    "Markdown",
    "Message",
    "Poll",
    "PollAnswer",
    "PollMediaAnswer",
    "PollMediaQuestion",
    "Timestamp",
    "TimestampStyles",
    "TopLevelComponent",
    "AllowedMentions",
    "AllowedMentionTypes",
    "Webhook",
]
