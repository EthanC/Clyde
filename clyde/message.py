"""Define the Message response object."""

from typing import Any

import msgspec
from msgspec import UNSET, Struct, UnsetType


class Message(Struct, kw_only=True):
    """
    Represent a message sent in a Discord channel.

    https://discord.com/developers/docs/resources/message#message-object

    Attributes:
        id (str): ID of the message.

        channel_id (str): ID of the channel the message was sent in.

        author (dict[str, Any]): Author of the message.

        content (str): Contents of the message.

        timestamp (str): ISO8601 timestamp for when the message was sent.

        edited_timestamp (str | None): ISO8601 timestamp for the most recent edit.

        tts (bool): Whether the message was text-to-speech.

        mention_everyone (bool): Whether the message mentions everyone.

        mentions (list[dict[str, Any]]): Users specifically mentioned.

        mention_roles (list[str]): Roles specifically mentioned.

        attachments (list[dict[str, Any]]): Files attached to the message.

        embeds (list[dict[str, Any]]): Embedded content in the message.

        pinned (bool): Whether the message is pinned.

        type (int): Type of the message.

        webhook_id (str): ID of the Webhook that generated the message.

        flags (int): Message Flags combined as a bitfield.

        components (list[dict[str, Any]]): Components included in the message.
    """

    id: str = msgspec.field()
    """ID of the message."""

    channel_id: str = msgspec.field()
    """ID of the channel the message was sent in."""

    author: dict[str, Any] = msgspec.field()
    """Author of the message."""

    content: str = msgspec.field()
    """Contents of the message."""

    timestamp: str = msgspec.field()
    """ISO8601 timestamp for when the message was sent."""

    edited_timestamp: str | None = msgspec.field()
    """ISO8601 timestamp for the most recent edit, or None if never edited."""

    tts: bool = msgspec.field()
    """Whether the message was text-to-speech."""

    mention_everyone: bool = msgspec.field()
    """Whether the message mentions everyone."""

    mentions: list[dict[str, Any]] = msgspec.field()
    """Users specifically mentioned in the message."""

    mention_roles: list[str] = msgspec.field()
    """Roles specifically mentioned in the message."""

    attachments: list[dict[str, Any]] = msgspec.field()
    """Files attached to the message."""

    embeds: list[dict[str, Any]] = msgspec.field()
    """Embedded content in the message."""

    pinned: bool = msgspec.field()
    """Whether the message is pinned."""

    type: int = msgspec.field()
    """Type of the message."""

    mention_channels: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Channels specifically mentioned in the message."""

    reactions: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Reactions to the message."""

    nonce: UnsetType | int | str = msgspec.field(default=UNSET)
    """Value used to validate that the message was sent."""

    webhook_id: UnsetType | str = msgspec.field(default=UNSET)
    """ID of the Webhook that generated the message."""

    activity: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Rich Presence-related message activity."""

    application: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Application associated with Rich Presence-related content."""

    application_id: UnsetType | str = msgspec.field(default=UNSET)
    """ID of the application associated with the message."""

    flags: UnsetType | int = msgspec.field(default=UNSET)
    """Message Flags combined as a bitfield."""

    message_reference: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Data identifying a message referenced by this message."""

    message_snapshots: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Snapshots associated with a forwarded message."""

    referenced_message: UnsetType | None | dict[str, Any] = msgspec.field(default=UNSET)
    """Message associated with the message reference."""

    interaction_metadata: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Metadata for the interaction that produced the message."""

    interaction: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Deprecated interaction data associated with the message."""

    thread: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Thread started from the message."""

    components: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Components included in the message."""

    sticker_items: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Stickers included in the message."""

    stickers: UnsetType | list[dict[str, Any]] = msgspec.field(default=UNSET)
    """Deprecated full sticker objects included in the message."""

    position: UnsetType | int = msgspec.field(default=UNSET)
    """Approximate position of the message in a thread."""

    role_subscription_data: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Role subscription data associated with the message."""

    resolved: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Users, members, channels, and roles referenced by the message."""

    poll: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Poll included in the message."""

    call: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Call associated with the message."""

    shared_client_theme: UnsetType | dict[str, Any] = msgspec.field(default=UNSET)
    """Custom client-side theme shared by the message."""
