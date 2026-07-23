"""Define constants shared across the Clyde package."""

from typing import Final

EMBED_IMAGE_MAX_COUNT: Final[int] = 4
"""Maximum number of images allowed in an Embed image gallery."""

ATTACHMENT_DESCRIPTION_MAX_LENGTH: Final[int] = 1024
"""
Maximum number of characters allowed in an Attachment description.

https://docs.discord.com/developers/resources/message#attachment-object
"""

MESSAGE_EMBED_MAX_COUNT: Final[int] = 10
"""
Maximum total number of Embeds allowed in a message.

https://docs.discord.com/developers/resources/message#embed-object-embed-limits
"""

MESSAGE_COMPONENT_MAX_COUNT: Final[int] = 40
"""
Maximum total number of Components allowed in a Components V2 message.

https://docs.discord.com/developers/change-log#raised-component-limits
"""
