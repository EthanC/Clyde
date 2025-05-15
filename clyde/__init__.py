"""
A modern, type-hinted Python library for seamless interaction with the Discord Webhook API.

https://github.com/EthanC/Clyde
"""

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
from clyde.poll import Poll, PollAnswer, PollMediaAnswer, PollMediaQuestion
from clyde.timestamp import Timestamp, TimestampStyles
from clyde.webhook import (
    AllowedMentions,
    AllowedMentionTypes,
    TopLevelComponent,
    Webhook,
)

__all__: list[str] = [
    "Component",
    "Embed",
    "EmbedAuthor",
    "EmbedField",
    "EmbedFooter",
    "EmbedImage",
    "EmbedThumbnail",
    "Markdown",
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
