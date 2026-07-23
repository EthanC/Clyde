"""Define constants shared across the Clyde package."""

from typing import Final

ATTACHMENT_DESCRIPTION_MAX_LENGTH: Final[int] = 1024
"""
Maximum number of characters allowed in an Attachment description.

https://docs.discord.com/developers/resources/message#attachment-object
"""

MESSAGE_COMPONENT_MAX_COUNT: Final[int] = 40
"""
Maximum total number of Components allowed in a Components V2 message.

https://docs.discord.com/developers/change-log#raised-component-limits
"""
