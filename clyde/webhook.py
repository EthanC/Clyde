"""Define the Webhook class and its associates."""

import logging
from asyncio import sleep as async_sleep
from base64 import b64encode
from enum import IntEnum, StrEnum
from pathlib import Path
from time import sleep
from typing import Annotated, Any, Final, Iterable, Literal, Self, TypeAlias
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from weakref import ReferenceType, ref

import msgspec
import niquests
from msgspec import UNSET, Meta, Struct, UnsetType
from niquests import AsyncSession, Response, Session

from clyde.attachment import Attachment
from clyde.component import (
    Component,
    _count_component_occurrences,
    _count_components,
    _iter_components,
    _register_component_owner,
    _unregister_component_owner,
)
from clyde.components.action_row import ActionRow
from clyde.components.container import Container
from clyde.components.file import File
from clyde.components.media_gallery import MediaGallery
from clyde.components.section import Section
from clyde.components.seperator import Seperator
from clyde.components.text_display import TextDisplay
from clyde.constants import (
    ATTACHMENT_DESCRIPTION_MAX_LENGTH,
    MESSAGE_COMPONENT_MAX_COUNT,
    MESSAGE_EMBED_MAX_COUNT,
)
from clyde.embed import Embed
from clyde.message import Message
from clyde.poll import Poll
from clyde.validation import Validation

TopLevelComponent: TypeAlias = (
    ActionRow | Container | File | MediaGallery | Section | Seperator | TextDisplay
)
TopLevelComponents: TypeAlias = list[TopLevelComponent]
_Avatar: TypeAlias = UnsetType | None | str | bytes | Path

_EXECUTE_PAYLOAD_FIELDS: tuple[str, ...] = (
    "content",
    "username",
    "avatar_url",
    "tts",
    "embeds",
    "allowed_mentions",
    "components",
    "flags",
    "thread_name",
    "applied_tags",
    "poll",
)
_EDIT_PAYLOAD_FIELDS: tuple[str, ...] = (
    "content",
    "embeds",
    "allowed_mentions",
    "components",
    "flags",
    "poll",
)
_EXECUTE_QUERY_FIELDS: tuple[str, ...] = ("wait", "thread_id", "with_components")
_EDIT_QUERY_FIELDS: tuple[str, ...] = ("thread_id", "with_components")
_MESSAGE_QUERY_FIELDS: tuple[str, ...] = ("thread_id",)
_OWNED_COMPONENTS_KEY: Final[str] = "_clyde_owned_components"
_AVATAR_MEDIA_TYPES: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)


class _AttachmentRequest(Struct, kw_only=True):
    """Represent attachment metadata in a Discord message request."""

    id: str | int = msgspec.field()
    """Existing Attachment ID or numeric placeholder for a new upload."""

    filename: UnsetType | str = msgspec.field(default=UNSET)
    """Name of a newly uploaded file."""

    description: (
        UnsetType | Annotated[str, Meta(max_length=ATTACHMENT_DESCRIPTION_MAX_LENGTH)]
    ) = msgspec.field(default=UNSET)
    """Description (alt text) for the Attachment."""

    is_spoiler: UnsetType | bool = msgspec.field(default=UNSET)
    """Whether the file should be a spoiler (blurred)."""


class AllowedMentionTypes(StrEnum):
    """
    Define the available types to be used in an Allowed Mentions object.

    https://discord.com/developers/docs/resources/message#allowed-mentions-object

    Attributes:
        ROLE_MENTIONS (str): Controls role mentions.

        USER_MENTIONS (str): Controls user mentions.

        EVERYONE_MENTIONS (str): Controls @everyone and @here mentions.
    """

    ROLE_MENTIONS = "roles"
    """Controls role mentions."""

    USER_MENTIONS = "users"
    """Controls user mentions."""

    EVERYONE_MENTIONS = "everyone"
    """Controls @everyone and @here mentions."""


class AllowedMentions(Struct, kw_only=True):
    """
    Represent the Allowed Mentions object on a Discord message.

    The Allowed Mention field allows for more granular control over mentions. This will
    always validate against the message and Components to avoid phantom pings. If
    allowed_mentions is not passed in, the mentions will be parsed via the content.

    https://discord.com/developers/docs/resources/message#allowed-mentions-object
    """

    parse: UnsetType | list[AllowedMentionTypes] = msgspec.field(default=UNSET)
    """An array of Allowed Mention Types to parse from the content."""

    roles: UnsetType | Annotated[list[str], Meta(min_length=1, max_length=100)] = (
        msgspec.field(default=UNSET)
    )
    """Array of role_ids to mention (max size of 100)."""

    users: UnsetType | Annotated[list[str], Meta(min_length=1, max_length=100)] = (
        msgspec.field(default=UNSET)
    )
    """Array of user_ids to mention (max size of 100)."""

    replied_user: UnsetType | bool = msgspec.field(default=UNSET)
    """For replies, whether to mention the author of the message being replied to."""

    def add_parse(
        self: Self, parse: AllowedMentionTypes | list[AllowedMentionTypes]
    ) -> "AllowedMentions":
        """
        Add an Allowed Mention Type to parse from the content.

        Arguments:
            parse (AllowedMentionTypes | list[AllowedMentionTypes]): An Allowed Mention
                Type or list of Allowed Mention Types to add.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if parse == AllowedMentionTypes.USER_MENTIONS and self.users:
            # No need for USER_MENTIONS if we already have users
            return self
        elif parse == AllowedMentionTypes.ROLE_MENTIONS and self.roles:
            # No need for ROLE_MENTIONS if we already have roles
            return self

        if isinstance(self.parse, UnsetType):
            self.parse = []

        if isinstance(parse, list):
            self.parse.extend(parse)
        else:
            self.parse.append(parse)

        return self

    def remove_parse(
        self: Self, parse: AllowedMentionTypes | list[AllowedMentionTypes] | int
    ) -> "AllowedMentions":
        """
        Remove an Allowed Mention Type from the Allowed Mentions instance.

        Arguments:
            parse (AllowedMentionTypes | list[AllowedMentionTypes] | int): An Allowed
                Mention Type, list of Allowed Mention Types, or an index to remove.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if isinstance(self.parse, list):
            if isinstance(parse, AllowedMentionTypes):
                self.parse.remove(parse)
            elif isinstance(parse, int):
                self.parse.pop(parse)
            else:
                self.parse = [entry for entry in self.parse if entry not in parse]

            # Do not retain an empty list
            if len(self.parse) == 0:
                self.parse = UNSET

        return self

    def add_role(self: Self, role: str | list[str]) -> "AllowedMentions":
        """
        Add a role ID to mention.

        Arguments:
            role (str | list[str]): A role ID or list of role IDs to add.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if (
            isinstance(self.parse, list)
            and AllowedMentionTypes.ROLE_MENTIONS in self.parse
        ):
            # No need for role if we already have ROLE_MENTIONS
            return self

        if isinstance(self.roles, UnsetType):
            self.roles = []

        if isinstance(role, list):
            self.roles.extend(role)
        else:
            self.roles.append(role)

        return self

    def remove_role(self: Self, role: str | list[str] | int) -> "AllowedMentions":
        """
        Remove a role ID from the Allowed Mentions instance.

        Arguments:
            role (str | list[str] | int): A role ID, list of role IDs, or an index
                to remove.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if isinstance(self.roles, list):
            if isinstance(role, str):
                self.roles.remove(role)
            elif isinstance(role, int):
                self.roles.pop(role)
            else:
                self.roles = [entry for entry in self.roles if entry not in role]

            # Do not retain an empty list
            if len(self.roles) == 0:
                self.roles = UNSET

        return self

    def add_user(self: Self, user: str | list[str]) -> "AllowedMentions":
        """
        Add a user ID to mention.

        Arguments:
            user (str | list[str]): A user ID or list of user IDs to add.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if (
            isinstance(self.parse, list)
            and AllowedMentionTypes.USER_MENTIONS in self.parse
        ):
            # No need for user if we already have USER_MENTIONS
            return self

        if isinstance(self.users, UnsetType):
            self.users = []

        if isinstance(user, list):
            self.users.extend(user)
        else:
            self.users.append(user)

        return self

    def remove_user(self: Self, user: str | list[str] | int) -> "AllowedMentions":
        """
        Remove a user ID from the Allowed Mentions instance.

        Arguments:
            user (str | list[str] | int): A user ID, list of user IDs, or an index
                to remove.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if isinstance(self.users, list):
            if isinstance(user, str):
                self.users.remove(user)
            elif isinstance(user, int):
                self.users.pop(user)
            else:
                self.users = [entry for entry in self.users if entry not in user]

            # Do not retain an empty list
            if len(self.users) == 0:
                self.users = UNSET

        return self

    def set_replied_user(self: Self, replied_user: bool) -> "AllowedMentions":
        """
        Set whether to mention the author of the message being replied to.

        Arguments:
            replied_user (bool): True to mention the author.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        self.replied_user = replied_user

        return self


class MessageFlags(IntEnum):
    """
    Define the available Flags to be set on a Discord message.

    https://discord.com/developers/docs/resources/message#message-object-message-flags

    Attributes:
        SUPPRESS_EMBEDS (int): Do not include any Embeds when serializing this message.

        SUPPRESS_NOTIFICATIONS (int): This message will not trigger push and desktop notifications.

        IS_COMPONENTS_V2 (int): Allows you to create fully Component-driven messages.
    """

    SUPPRESS_EMBEDS = 1 << 2
    """Do not include any Embeds when serializing this message."""

    SUPPRESS_NOTIFICATIONS = 1 << 12
    """This message will not trigger push and desktop notifications."""

    IS_COMPONENTS_V2 = 1 << 15
    """Allows you to create fully Component-driven messages."""


class Webhook(Struct, kw_only=True, dict=True, weakref=True):
    """
    Represent a Discord Webhook object.

    Webhooks are a low-effort way to post messages to channels in Discord. They do not
    require a bot user or authentication to use.

    https://discord.com/developers/docs/resources/webhook

    Attributes:
        url (str): The URL used for executing the Webhook (returned by the Webhooks OAuth2 flow).

        id (str): The ID of the Webhook.

        type (int): The type of the Webhook.

        guild_id (str | None): The guild id this Webhook is for, if any.

        channel_id (str | None): The channel id this Webhook is for, if any.

        name (str | None): The default name of the Webhook.

        avatar (str | None): The default user avatar hash of the Webhook.

        token (str): The secure token of the Webhook (returned for Incoming Webhooks).

        application_id (str | None): The bot/OAuth2 application that created this Webhook.

        content (str): The message contents (up to 2000 characters).

        username (str): Override the default username of the Webhook.

        avatar_url (str): Override the default avatar of the Webhook.

        tts (bool): True if this is a TTS message.

        embeds (list[Embed]): Embedded rich content.

        allowed_mentions (AllowedMentions): Allowed mentions for the message.

        components (list[TopLevelComponent]): The Components to include with the
            message.

        flags (int): Message Flags combined as a bitfield.

        thread_name (str): Name of thread to create (requires the Webhook channel
            to be a forum or media channel).

        applied_tags (list[str]): Array of tag ids to apply to the thread (requires
            the Webhook channel to be a forum or media channel).

        poll (Poll): A Poll!

        _attachments (list[Attachment]): Attachment objects to include with the
            payload.

        _query_params (dict[str, str]): Additional query parameters to append to
            the URL.
    """

    url: str = msgspec.field()
    """the url used for executing the Webhook (returned by the Webhooks OAuth2 flow)."""

    id: UnsetType | str = msgspec.field(default=UNSET)
    """The ID of the Webhook."""

    type: UnsetType | int = msgspec.field(default=UNSET)
    """The type of the Webhook."""

    guild_id: UnsetType | None | str = msgspec.field(default=UNSET)
    """The guild id this Webhook is for, if any."""

    channel_id: UnsetType | None | str = msgspec.field(default=UNSET)
    """The channel id this Webhook is for, if any."""

    name: UnsetType | None | str = msgspec.field(default=UNSET)
    """The default name of the Webhook."""

    avatar: UnsetType | None | str = msgspec.field(default=UNSET)
    """The default user avatar hash of the Webhook."""

    token: UnsetType | str = msgspec.field(default=UNSET)
    """The secure token of the Webhook (returned for Incoming Webhooks)."""

    application_id: UnsetType | None | str = msgspec.field(default=UNSET)
    """The bot/OAuth2 application that created this Webhook."""

    content: UnsetType | None | Annotated[str, Meta(max_length=2000)] = msgspec.field(
        default=UNSET
    )
    """The message contents (up to 2000 characters)."""

    username: UnsetType | str = msgspec.field(default=UNSET)
    """Override the default username of the Webhook."""

    avatar_url: UnsetType | str = msgspec.field(default=UNSET)
    """Override the default avatar of the Webhook."""

    tts: UnsetType | bool = msgspec.field(default=UNSET)
    """True if this is a TTS message."""

    embeds: (
        UnsetType
        | None
        | Annotated[list[Embed], Meta(max_length=MESSAGE_EMBED_MAX_COUNT)]
    ) = msgspec.field(default=UNSET)
    """Embedded rich content."""

    allowed_mentions: UnsetType | None | AllowedMentions = msgspec.field(default=UNSET)
    """Allowed mentions for the message."""

    components: UnsetType | None | list[TopLevelComponent] = msgspec.field(
        default=UNSET
    )
    """The Components to include with the message."""

    flags: UnsetType | None | int = msgspec.field(default=UNSET)
    """Message Flags combined as a bitfield."""

    thread_name: UnsetType | str = msgspec.field(default=UNSET)
    """Name of thread to create (requires the Webhook channel to be a forum or media channel)."""

    applied_tags: UnsetType | list[str] = msgspec.field(default=UNSET)
    """Array of tag ids to apply to the thread (requires the Webhook channel to be a forum or media channel)."""

    poll: UnsetType | Poll = msgspec.field(default=UNSET)
    """A Poll!"""

    _attachments: list[Attachment] = []
    """Attachment objects to include with the payload."""

    _attachment_manifest: UnsetType | list[_AttachmentRequest] = UNSET
    """Existing Attachments to retain when editing a message."""

    _query_params: dict[str, str] = {}
    """Additional query parameters to append to the URL."""

    def __post_init__(self: Self) -> None:
        """Register this Webhook with its initial Component tree."""
        self._sync_component_owners()

    def __copy__(self: Self) -> Self:
        """Create a shallow copy with rebuilt Component ownership state."""
        return msgspec.structs.replace(self)

    def execute(self: Self) -> Response:
        """
        Execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.

        Raises:
            ValueError: The Webhook has no content, Embeds, Components, file, or Poll.
        """
        self._validate()

        req: dict[str, Any] = self._build_request(
            _EXECUTE_PAYLOAD_FIELDS, _EXECUTE_QUERY_FIELDS
        )

        return self._send_request("POST", self._base_url(), req)

    async def execute_async(self: Self) -> Response:
        """
        Asynchronously execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.

        Raises:
            ValueError: The Webhook has no content, Embeds, Components, file, or Poll.
        """
        self._validate()

        req: dict[str, Any] = self._build_request(
            _EXECUTE_PAYLOAD_FIELDS, _EXECUTE_QUERY_FIELDS
        )

        return await self._send_request_async("POST", self._base_url(), req)

    def get(self: Self) -> "Webhook":
        """
        Get the current Webhook using its token.

        https://docs.discord.com/developers/resources/webhook#get-webhook-with-token

        Returns:
            webhook (Webhook): Webhook populated with Discord's response data.
        """
        res: Response = self._send_request("GET", self._base_url(), {})

        return self._decode_webhook(res)

    async def get_async(self: Self) -> "Webhook":
        """
        Asynchronously get the current Webhook using its token.

        https://docs.discord.com/developers/resources/webhook#get-webhook-with-token

        Returns:
            webhook (Webhook): Webhook populated with Discord's response data.
        """
        res: Response = await self._send_request_async("GET", self._base_url(), {})

        return self._decode_webhook(res)

    def modify(
        self: Self,
        *,
        name: UnsetType | str = UNSET,
        avatar: _Avatar = UNSET,
        reason: str | None = None,
    ) -> Response:
        """
        Modify the current Webhook using its token.

        Fields left as ``UNSET`` remain unchanged. Set ``avatar`` to ``None`` to
        clear the default avatar; otherwise, provide Discord-compatible image data.

        https://docs.discord.com/developers/resources/webhook#modify-webhook-with-token

        Arguments:
            name (str): New default name for the Webhook.

            avatar (str | bytes | Path | None): New default avatar as an image data URI,
                image bytes, or image file path. Set to ``None`` to clear it.

            reason (str | None): Optional audit log reason (1-512 characters).

        Returns:
            res (Response): Response object containing the modified Webhook.
        """
        req: dict[str, Any] = self._modify_request(name, avatar, reason)

        return self._send_request("PATCH", self._base_url(), req)

    async def modify_async(
        self: Self,
        *,
        name: UnsetType | str = UNSET,
        avatar: _Avatar = UNSET,
        reason: str | None = None,
    ) -> Response:
        """
        Asynchronously modify the current Webhook using its token.

        Fields left as ``UNSET`` remain unchanged. Set ``avatar`` to ``None`` to
        clear the default avatar; otherwise, provide Discord-compatible image data.

        https://docs.discord.com/developers/resources/webhook#modify-webhook-with-token

        Arguments:
            name (str): New default name for the Webhook.

            avatar (str | bytes | Path | None): New default avatar as an image data URI,
                image bytes, or image file path. Set to ``None`` to clear it.

            reason (str | None): Optional audit log reason (1-512 characters).

        Returns:
            res (Response): Response object containing the modified Webhook.
        """
        req: dict[str, Any] = self._modify_request(name, avatar, reason)

        return await self._send_request_async("PATCH", self._base_url(), req)

    def delete(self: Self, reason: str | None = None) -> Response:
        """
        Permanently delete the current Webhook using its token.

        https://docs.discord.com/developers/resources/webhook#delete-webhook-with-token

        Arguments:
            reason (str | None): Optional audit log reason (1-512 characters).

        Returns:
            res (Response): Response object for the deletion request.
        """
        return self._send_request(
            "DELETE", self._base_url(), self._audit_log_request(reason)
        )

    async def delete_async(self: Self, reason: str | None = None) -> Response:
        """
        Asynchronously and permanently delete the current Webhook using its token.

        https://docs.discord.com/developers/resources/webhook#delete-webhook-with-token

        Arguments:
            reason (str | None): Optional audit log reason (1-512 characters).

        Returns:
            res (Response): Response object for the deletion request.
        """
        return await self._send_request_async(
            "DELETE", self._base_url(), self._audit_log_request(reason)
        )

    def get_message(self: Self, message_id: str) -> Message:
        """
        Get a message previously sent by this Webhook.

        https://discord.com/developers/docs/resources/webhook#get-webhook-message

        Arguments:
            message_id (str): ID of the message to retrieve.

        Returns:
            message (Message): Message populated with Discord's response data.
        """
        self._validate_message_id(message_id)

        res: Response = self._send_request(
            "GET",
            self._message_url(message_id),
            {"params": self._build_query_params(_MESSAGE_QUERY_FIELDS)},
        )

        return self._decode_message(res)

    async def get_message_async(self: Self, message_id: str) -> Message:
        """
        Asynchronously get a message previously sent by this Webhook.

        https://discord.com/developers/docs/resources/webhook#get-webhook-message

        Arguments:
            message_id (str): ID of the message to retrieve.

        Returns:
            message (Message): Message populated with Discord's response data.
        """
        self._validate_message_id(message_id)

        res: Response = await self._send_request_async(
            "GET",
            self._message_url(message_id),
            {"params": self._build_query_params(_MESSAGE_QUERY_FIELDS)},
        )

        return self._decode_message(res)

    def edit_message(self: Self, message_id: str) -> Response:
        """
        Edit a message previously sent by this Webhook.

        Fields left as ``UNSET`` remain unchanged. Use ``None`` for nullable fields and
        empty lists for arrays to clear existing values.
        When adding Components to a legacy message, explicitly clear its existing
        content and Embeds as required by Discord. Existing Attachments may remain
        when retained and referenced by a compatible Component.
        Before uploading files, call ``retain_attachment`` for every existing file that
        should remain, or call ``clear_attachments`` before adding replacement files.

        https://discord.com/developers/docs/resources/webhook#edit-webhook-message

        Arguments:
            message_id (str): ID of the message to edit.

        Returns:
            res (Response): Response object containing the edited message.
        """
        self._validate(edit=True)
        self._validate_edit(message_id)

        req: dict[str, Any] = self._build_request(
            _EDIT_PAYLOAD_FIELDS, _EDIT_QUERY_FIELDS, edit=True
        )

        return self._send_request("PATCH", self._message_url(message_id), req)

    async def edit_message_async(self: Self, message_id: str) -> Response:
        """
        Asynchronously edit a message previously sent by this Webhook.

        Fields left as ``UNSET`` remain unchanged. Use ``None`` for nullable fields and
        empty lists for arrays to clear existing values.
        When adding Components to a legacy message, explicitly clear its existing
        content and Embeds as required by Discord. Existing Attachments may remain
        when retained and referenced by a compatible Component.
        Before uploading files, call ``retain_attachment`` for every existing file that
        should remain, or call ``clear_attachments`` before adding replacement files.

        https://discord.com/developers/docs/resources/webhook#edit-webhook-message

        Arguments:
            message_id (str): ID of the message to edit.

        Returns:
            res (Response): Response object containing the edited message.
        """
        self._validate(edit=True)
        self._validate_edit(message_id)

        req: dict[str, Any] = self._build_request(
            _EDIT_PAYLOAD_FIELDS, _EDIT_QUERY_FIELDS, edit=True
        )

        return await self._send_request_async(
            "PATCH", self._message_url(message_id), req
        )

    def set_content(
        self: Self, content: UnsetType | None | str, fallback: bool = False
    ) -> "Webhook":
        """
        Set the message content of the Webhook.

        Arguments:
            content (str | None): Message content. If set to None, the message content
                is cleared.
            fallback (bool): Set the content as a file Attachment if the message
                length limit is exceeded.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if fallback and isinstance(content, str):
            max_len: int | None = Validation.get_max_length(Webhook, "content")

            if isinstance(max_len, int) and (len(content) > max_len):
                self.add_attachment("message.txt", content.encode())

                return self

        self.content = content

        return self

    def set_username(self: Self, username: UnsetType | str) -> "Webhook":
        """
        Set the username of the Webhook instance.

        Arguments:
            username (str): A username. If set to None, the username is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.username = username

        return self

    def set_avatar_url(self: Self, avatar_url: UnsetType | str) -> "Webhook":
        """
        Set the avatar URL of the Webhook instance.

        Arguments:
            avatar_url (str): An image URL. If set to None, the avatar_url is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.avatar_url = avatar_url

        return self

    def set_tts(self: Self, tts: UnsetType | bool) -> "Webhook":
        """
        Set whether the Webhook instance is a text-to-speech message.

        Arguments:
            tts (bool): Toggle text-to-speech functionality.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.tts = tts

        return self

    def add_embed(self: Self, embed: Embed | list[Embed]) -> "Webhook":
        """
        Add embedded rich content to the Webhook instance.

        Arguments:
            embed (Embed | list[Embed]): An Embed or list of Embeds.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if not isinstance(self.embeds, list):
            self.embeds = []

        if isinstance(embed, Embed):
            self.embeds.append(embed)
        else:
            self.embeds.extend(embed)

        return self

    def remove_embed(self: Self, embed: Embed | list[Embed] | int | None) -> "Webhook":
        """
        Remove embedded rich content from the Webhook instance.

        Arguments:
            embed (Embed | list[Embed] | int | None): An Embed, list of Embeds, or an
                index to remove. If set to None, all Embeds are cleared from an edited
                message.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if embed is None:
            self.embeds = []
        elif isinstance(self.embeds, list):
            if isinstance(embed, Embed):
                self.embeds.remove(embed)
            elif isinstance(embed, int):
                self.embeds.pop(embed)
            else:
                self.embeds = [entry for entry in self.embeds if entry not in embed]

            # Do not retain an empty list
            if len(self.embeds) == 0:
                self.embeds = UNSET

        return self

    def set_allowed_mentions(
        self: Self, allowed_mentions: UnsetType | None | AllowedMentions
    ) -> "Webhook":
        """
        Set the allowed mentions for the Webhook instance.

        Arguments:
            allowed_mentions (AllowedMentions | None): An Allowed Mentions object. If set
                to None, the allowed_mentions value is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.allowed_mentions = allowed_mentions

        return self

    def add_component(
        self: Self, component: TopLevelComponent | Iterable[TopLevelComponent]
    ) -> "Webhook":
        """
        Add a Component to the Webhook instance.

        Arguments:
            component (TopLevelComponent | Iterable[TopLevelComponent]): A Component or
                an iterable of Components.

        Returns:
            self (Webhook): The modified Webhook instance.

        Raises:
            ValueError: The addition would exceed the 40 total Component limit.
        """
        components: list[TopLevelComponent]

        if isinstance(component, TopLevelComponent):
            components = [component]
        else:
            components = list(component)

        self._sync_component_owners()

        current_components: list[TopLevelComponent] = (
            self.components if isinstance(self.components, list) else []
        )

        self._validate_component_count(
            _count_components(current_components) + _count_components(components)
        )

        self.components = [*current_components, *components]

        self.set_flag(MessageFlags.IS_COMPONENTS_V2, True)
        self._sync_component_owners()

        return self

    def remove_component(
        self: Self, component: TopLevelComponent | list[TopLevelComponent] | int | None
    ) -> "Webhook":
        """
        Remove a Component from the Webhook instance.

        Arguments:
            component (TopLevelComponent | list[TopLevelComponent] | int | None): A
                Component, list of Components, or an index to remove. If set to None,
                all Components are cleared from an edited message.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if component is None:
            self.components = []
        elif isinstance(self.components, list):
            components: list[TopLevelComponent] = self.components.copy()

            if isinstance(component, TopLevelComponent):
                components.remove(component)
            elif isinstance(component, int):
                components.pop(component)
            else:
                components = [entry for entry in components if entry not in component]

            # Do not retain an empty list
            if len(components) == 0:
                self.components = UNSET
            else:
                self.components = components

        self._sync_component_owners()

        return self

    def add_attachment(
        self: Self,
        filename: str,
        content: bytes | Path,
        *,
        spoiler: bool = False,
        description: UnsetType | str = UNSET,
    ) -> "Webhook":
        """
        Add a file Attachment to the Webhook instance.

        Arguments:
            filename (str): Name of the file to attach.

            content (bytes | Path): Binary content of the file to attach.
                If a Path is passed, the referenced file will be read.

            spoiler (bool): True if the file should be a spoiler (blurred).

            description (str): Description or alt text for the file.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if isinstance(content, Path):
            with open(content, "rb") as handle:
                content = handle.read()

        attachment: Attachment = Attachment(filename=filename, content=content)

        if isinstance(description, str):
            attachment.set_description(description)

        if spoiler:
            attachment.set_spoiler(True)

        self._attachments.append(attachment)

        return self

    def retain_attachment(
        self: Self,
        attachment_id: str,
        *,
        description: UnsetType | str = UNSET,
        spoiler: UnsetType | bool = UNSET,
    ) -> "Webhook":
        """
        Retain an existing Attachment when editing a message.

        Discord treats an edit request's Attachment list as the complete set to keep.
        Call this method for every existing Attachment that should remain.

        Arguments:
            attachment_id (str): ID of an existing Attachment.

            description (str): Updated description or alt text.

            spoiler (bool): Updated spoiler state.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if not attachment_id:
            raise ValueError("attachment_id must not be empty")
        elif (
            isinstance(description, str)
            and len(description) > ATTACHMENT_DESCRIPTION_MAX_LENGTH
        ):
            raise ValueError("Attachment description must be 1024 or fewer characters")

        if not isinstance(self._attachment_manifest, list):
            self._attachment_manifest = []

        self._attachment_manifest = [
            attachment
            for attachment in self._attachment_manifest
            if attachment.id != attachment_id
        ]
        self._attachment_manifest.append(
            _AttachmentRequest(
                id=attachment_id, description=description, is_spoiler=spoiler
            )
        )

        return self

    def clear_attachments(self: Self) -> "Webhook":
        """
        Remove pending and existing Attachments when editing a message.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self._attachments = []
        self._attachment_manifest = []

        return self

    def remove_attachment(
        self: Self, attachment: Attachment | list[Attachment] | int | str
    ) -> "Webhook":
        """
        Remove a file Attachment from the Webhook instance.

        Arguments:
            attachment (Attachment | list[Attachment] | int | str): An Attachment,
                list of Attachments, an index, or a filename to remove.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if isinstance(attachment, Attachment):
            self._attachments.remove(attachment)
        elif isinstance(attachment, int):
            self._attachments.pop(attachment)
        elif isinstance(attachment, str):
            self._attachments = [
                entry for entry in self._attachments if entry.filename != attachment
            ]
        else:
            self._attachments = [
                entry for entry in self._attachments if entry not in attachment
            ]

        return self

    def set_flag(
        self: Self, flag: MessageFlags, value: Literal[True] | None
    ) -> "Webhook":
        """
        Set a Message Flag for the Webhook instance.

        Arguments:
            flag (MessageFlag): A Discord Message Flag.

            value (Literal[True] | None): Toggle the Message Flag. If set to None, the
                flag is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if not isinstance(self.flags, int):
            self.flags = 0

        if value:
            # Enable the Message Flag
            self.flags |= flag
        else:
            # Disable the Message Flag
            self.flags &= ~flag

        return self

    def get_flag(self: Self, flag: MessageFlags) -> bool:
        """
        Get the value of a Message Flag from the Webhook instance.

        Arguments:
            flag (MessageFlag): A Discord Message Flag.

        Returns:
            value (bool): The value of the Message Flag.
        """
        if isinstance(self.flags, int) and (self.flags & flag):
            return True

        return False

    def set_thread_name(self: Self, thread_name: UnsetType | str) -> "Webhook":
        """
        Set the name of the thread to create.

        Requires the Webhook channel to be a forum or media channel.

        Arguments:
            thread_name (str | None): A thread name. If set to None, the thread_name value
                is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.thread_name = thread_name

        return self

    def set_poll(self: Self, poll: Poll) -> "Webhook":
        """
        Set a Poll for the Webhook instance.

        Arguments:
            poll (Poll): A Discord Poll object. Editing a message can only add a Poll
                to a deferred interaction response.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.poll = poll

        return self

    def set_wait(self: Self, wait: bool | None) -> "Webhook":
        """
        Set whether to wait for the Webhook request response from Discord.

        Arguments:
            wait (bool | None): Toggle wait functionality. If set to None, the wait value
                is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        key: str = "wait"

        if wait is None:
            self._remove_query_param(key)
        else:
            self._query_params[key] = str(wait)

        return self

    def set_thread_id(self: Self, thread_id: str | None) -> "Webhook":
        """
        Set the thread to message within the Webhook's channel.

        Arguments:
            thread_id (str | None): A thread ID. If set to None, the thread_id value
                is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        key: str = "thread_id"

        if thread_id is None:
            self._remove_query_param(key)
        else:
            self._query_params[key] = thread_id

        return self

    def _validate(self: Self, edit: bool = False) -> None:
        """Convert applicable data types prior to Webhook serialization."""
        self._sync_component_owners()

        if not edit and not any(
            (
                isinstance(self.content, str) and bool(self.content),
                isinstance(self.embeds, list) and bool(self.embeds),
                isinstance(self.components, list) and bool(self.components),
                bool(self._valid_attachments()),
                isinstance(self.poll, Poll),
            )
        ):
            raise ValueError(
                "Webhook execution requires at least one of content, embeds, components, file, or poll"
            )

        if isinstance(self.embeds, list):
            embed_count: int = len(self._expand_embeds(self.embeds))

            if embed_count > MESSAGE_EMBED_MAX_COUNT:
                raise ValueError(
                    f"Webhook messages cannot contain more than {MESSAGE_EMBED_MAX_COUNT:,} Embeds after expanding image galleries"
                )

            for embed in self.embeds:
                if not isinstance(embed.color, UnsetType):
                    embed.color = Validation.convert_color(embed.color)

                if not isinstance(embed.timestamp, UnsetType):
                    embed.timestamp = Validation.convert_timestamp(embed.timestamp)

        if isinstance(self.components, list):
            for component in self.components:
                if isinstance(component, Container):
                    if not isinstance(component.accent_color, UnsetType):
                        component.accent_color = Validation.convert_color(
                            component.accent_color
                        )

        self._validate_components(edit)

    def _validate_components(self: Self, edit: bool) -> None:
        """Validate fields that cannot accompany Components."""
        if not (
            isinstance(self.flags, int) and self.flags & MessageFlags.IS_COMPONENTS_V2
        ):
            return

        components: list[TopLevelComponent] = (
            self.components if isinstance(self.components, list) else []
        )

        self._validate_component_count(_count_components(components))

        if edit and self.embeds is None:
            self.embeds = []

        incompatible_fields: dict[str, Any] = {
            "content": self.content,
            "embeds": self.embeds,
            "files[n]": self._valid_attachments(),
            "poll": self.poll,
        }
        incompatible_fields = {
            name: value
            for name, value in incompatible_fields.items()
            if not isinstance(value, UnsetType) and value is not None and value != []
        }

        if incompatible_fields:
            fields: str = ", ".join(incompatible_fields)
            raise ValueError(f"COMPONENTS cannot be combined with non-null {fields}")

    def _sync_component_owners(self: Self) -> None:
        """Synchronize non-serialized ownership for the current Component tree."""
        previous_references: list[ReferenceType[Component]] = self.__dict__.get(
            _OWNED_COMPONENTS_KEY, []
        )
        previous_components: list[Component] = []

        for reference in previous_references:
            component: Component | None = reference()

            if component is not None:
                previous_components.append(component)

        _unregister_component_owner(previous_components, self)

        current_components: list[Component] = (
            list(_iter_components(self.components))
            if isinstance(self.components, list)
            else []
        )

        _register_component_owner(current_components, self)

        current_references: list[ReferenceType[Component]] = [
            ref(component) for component in current_components
        ]
        self.__dict__[_OWNED_COMPONENTS_KEY] = current_references

    def _component_occurrences(self: Self, component: Component) -> int:
        """Return the number of times a Component occurs in this message tree."""
        if not isinstance(self.components, list):
            return 0

        return _count_component_occurrences(self.components, component)

    def _validate_nested_component_addition(
        self: Self, parent: Component, components: Iterable[Component]
    ) -> None:
        """Validate a nested addition against this message's total count."""
        if not self.get_flag(MessageFlags.IS_COMPONENTS_V2):
            return

        current_components: list[TopLevelComponent] = (
            self.components if isinstance(self.components, list) else []
        )
        projected_count: int = _count_components(current_components) + (
            self._component_occurrences(parent) * _count_components(components)
        )

        self._validate_component_count(projected_count)

    @staticmethod
    def _validate_component_count(component_count: int) -> None:
        """Validate a Components V2 message's total Component count."""
        if component_count > MESSAGE_COMPONENT_MAX_COUNT:
            raise ValueError(
                "Components V2 messages cannot contain more than "
                f"{MESSAGE_COMPONENT_MAX_COUNT} total Components"
            )

    def _validate_edit(self: Self, message_id: str) -> None:
        """Validate fields specific to editing a Webhook message."""
        self._validate_message_id(message_id)

        allowed_flags: int = (
            MessageFlags.SUPPRESS_EMBEDS | MessageFlags.IS_COMPONENTS_V2
        )
        if isinstance(self.flags, int) and self.flags & ~allowed_flags:
            raise ValueError(
                "Webhook message edits only support SUPPRESS_EMBEDS and IS_COMPONENTS_V2 flags"
            )

        if self._attachments and not isinstance(self._attachment_manifest, list):
            raise ValueError(
                "Call retain_attachment() or clear_attachments() before uploading files in a message edit"
            )

    @staticmethod
    def _validate_message_id(message_id: str) -> None:
        """Validate a Webhook message ID."""
        if not message_id:
            raise ValueError("message_id must not be empty")

    def _decode_webhook(self: Self, res: Response) -> "Webhook":
        """Decode a Webhook response and retain its executable URL."""
        data: dict[str, Any] = msgspec.json.decode(
            res.content or b"", type=dict[str, Any]
        )
        data.setdefault("url", self._base_url())

        return msgspec.convert(data, type=Webhook)

    @staticmethod
    def _decode_message(res: Response) -> Message:
        """Decode a Message response."""
        return msgspec.json.decode(res.content or b"", type=Message)

    def _base_url(self: Self) -> str:
        """Return the Webhook URL without query parameters or fragments."""
        parsed = urlsplit(self.url)
        return urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "")
        )

    @staticmethod
    def _modify_request(
        name: UnsetType | str, avatar: _Avatar, reason: str | None
    ) -> dict[str, Any]:
        """Return request arguments for modifying a Webhook with its token."""
        if isinstance(avatar, (bytes, Path)):
            avatar = Webhook._avatar_data(avatar)

        payload: dict[str, Any] = {
            key: value
            for key, value in {"name": name, "avatar": avatar}.items()
            if not isinstance(value, UnsetType)
        }
        headers: dict[str, str] = {"Content-Type": "application/json"}

        headers.update(Webhook._audit_log_request(reason).get("headers", {}))

        return {"data": msgspec.json.encode(payload), "headers": headers}

    @staticmethod
    def _avatar_data(avatar: bytes | Path) -> str:
        """Convert supported image bytes to Discord image data."""
        data: bytes = avatar.read_bytes() if isinstance(avatar, Path) else avatar
        media_type: str | None = next(
            (
                media_type
                for signature, media_type in _AVATAR_MEDIA_TYPES
                if data.startswith(signature)
            ),
            None,
        )
        if media_type is None:
            raise ValueError(
                "Webhook avatars must contain PNG, JPEG, or GIF image data"
            )

        return f"data:{media_type};base64,{b64encode(data).decode('ascii')}"

    @staticmethod
    def _audit_log_request(reason: str | None) -> dict[str, Any]:
        """Return request headers containing an optional audit log reason."""
        if reason is None:
            return {}
        elif not reason or len(reason) > 512:
            raise ValueError("Audit log reason must be between 1 and 512 characters")

        return {"headers": {"X-Audit-Log-Reason": quote(reason, safe="")}}

    def _remove_query_param(self: Self, key: str) -> None:
        """Remove a query parameter from stored and URL-provided state."""
        self._query_params.pop(key, None)
        parsed = urlsplit(self.url)
        query = urlencode(
            [(name, value) for name, value in parse_qsl(parsed.query) if name != key]
        )
        self.url = urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment)
        )

    def _message_url(self: Self, message_id: str) -> str:
        """Return the endpoint URL for a Webhook message."""
        return f"{self._base_url()}/messages/{message_id}"

    def _valid_attachments(self: Self) -> list[Attachment]:
        """Return local Attachments that contain a filename and content."""
        return [
            attachment
            for attachment in self._attachments
            if isinstance(attachment.filename, str)
            and isinstance(attachment.content, bytes)
        ]

    def _attachment_request(
        self: Self, attachment_id: int, attachment: Attachment
    ) -> _AttachmentRequest:
        """Build request metadata for a local Attachment."""
        return _AttachmentRequest(
            id=attachment_id,
            filename=attachment.filename,
            description=attachment.description,
            is_spoiler=attachment.spoiler,
        )

    def _build_payload(
        self: Self, payload_fields: tuple[str, ...], edit: bool
    ) -> dict[str, Any]:
        """Build an endpoint-specific Webhook payload."""
        payload: dict[str, Any] = {}
        for field in payload_fields:
            value: Any = getattr(self, field)
            if isinstance(value, UnsetType) or (
                not edit and (value is None or value == [])
            ):
                continue

            if field == "embeds" and isinstance(value, list):
                value = self._expand_embeds(value)

            payload[field] = value
        attachments: list[Attachment] = self._valid_attachments()
        attachment_requests: list[_AttachmentRequest] = [
            self._attachment_request(index, attachment)
            for index, attachment in enumerate(attachments)
        ]

        if edit and (
            isinstance(self._attachment_manifest, list) or attachment_requests
        ):
            retained_attachments: list[_AttachmentRequest] = (
                self._attachment_manifest
                if isinstance(self._attachment_manifest, list)
                else []
            )
            payload["attachments"] = [*retained_attachments, *attachment_requests]
        elif not edit and attachment_requests:
            payload["attachments"] = attachment_requests

        return payload

    @staticmethod
    def _expand_embeds(embeds: list[Embed]) -> list[Embed]:
        """Expand logical Embed image galleries into Discord payload Embeds."""
        return [
            payload_embed
            for embed in embeds
            for payload_embed in embed._payload_embeds()
        ]

    @staticmethod
    def _strip_internal_fields(value: Any) -> Any:
        """Remove msgspec discriminator fields from an outgoing payload."""
        if isinstance(value, dict):
            return {
                key: Webhook._strip_internal_fields(entry)
                for key, entry in value.items()
                if key != "_type"
            }
        elif isinstance(value, list):
            return [Webhook._strip_internal_fields(entry) for entry in value]

        return value

    def _build_request(
        self: Self,
        payload_fields: tuple[str, ...],
        query_fields: tuple[str, ...],
        edit: bool = False,
    ) -> dict[str, Any]:
        """Return request arguments for a Webhook operation."""
        payload: dict[str, Any] = self._build_payload(payload_fields, edit)
        payload_data: Any = msgspec.to_builtins(payload)
        payload_data = self._strip_internal_fields(payload_data)
        payload_json: bytes = msgspec.json.encode(payload_data)
        params: dict[str, str] = self._build_query_params(query_fields)
        if "components" in payload and "with_components" in query_fields:
            params["with_components"] = "True"
        attachments: list[Attachment] = self._valid_attachments()

        if attachments:
            files: dict[str, Any] = {"payload_json": (None, payload_json)}

            for index, attachment in enumerate(attachments):
                files[f"files[{index}]"] = (attachment.filename, attachment.content)

            return {"files": files, "params": params}

        return {
            "data": payload_json,
            "params": params,
            "headers": {"Content-Type": "application/json"},
        }

    def _build_query_params(
        self: Self, query_fields: tuple[str, ...]
    ) -> dict[str, str]:
        """Return endpoint-specific query parameters."""
        params: dict[str, str] = {
            key: value
            for key, value in parse_qsl(
                urlsplit(self.url).query, keep_blank_values=True
            )
            if key in query_fields
        }

        params.update(
            {
                key: value
                for key, value in self._query_params.items()
                if key in query_fields
            }
        )

        return params

    @staticmethod
    def _raise_for_status(
        response: Response, request: dict[str, Any] | None = None
    ) -> Response:
        """Raise an HTTP error enriched with details returned by Discord."""

        def flatten_errors(
            value: Any, path: str = "", payload_path: tuple[str, ...] = ()
        ) -> list[tuple[str, tuple[str, ...], str]]:
            if isinstance(value, dict):
                message: Any = value.get("message")

                if isinstance(message, str):
                    code: Any = value.get("code")
                    location: str = path

                    if isinstance(code, (int, str)):
                        location = f"{location}[{code}]" if location else f"[{code}]"

                    detail: str = f"{location}: {message}" if location else message

                    return [(path, payload_path, detail)]

                details: list[tuple[str, tuple[str, ...], str]] = []

                for key, entry in value.items():
                    if key == "_errors":
                        details.extend(flatten_errors(entry, path, payload_path))

                        continue

                    key = str(key)

                    if key.isdecimal():
                        next_path: str = f"{path}[{key}]" if path else f"[{key}]"
                    else:
                        next_path = f"{path}.{key}" if path else key

                    details.extend(
                        flatten_errors(entry, next_path, (*payload_path, key))
                    )

                return details

            elif isinstance(value, list):
                return [
                    detail
                    for entry in value
                    for detail in flatten_errors(entry, path, payload_path)
                ]
            elif isinstance(value, str):
                detail = f"{path}: {value}" if path else value

                return [(path, payload_path, detail)]

            return []

        try:
            return response.raise_for_status()
        except niquests.HTTPError as error:
            try:
                response_data: Any = response.json()
            except niquests.JSONDecodeError:
                pass
            else:
                if isinstance(response_data, dict):
                    message: Any = response_data.get("message")
                    code: Any = response_data.get("code")
                    error_data: Any = response_data.get("errors")

                    if error_data is None:
                        error_data = {
                            key: value
                            for key, value in response_data.items()
                            if key not in ("message", "code")
                        }

                    details: list[str] = []

                    if isinstance(message, str):
                        code_text: str = (
                            f" {code}" if isinstance(code, (int, str)) else ""
                        )

                        details.append(f"Discord API error{code_text}: {message}")

                    flattened_errors = flatten_errors(error_data)
                    details.extend(detail for _, _, detail in flattened_errors)

                    if request is not None:
                        payload_data: Any = request.get("data")

                        if payload_data is None:
                            files: Any = request.get("files")

                            if isinstance(files, dict):
                                payload_json: Any = files.get("payload_json")

                                if isinstance(payload_json, tuple):
                                    payload_data = payload_json[1]

                        try:
                            payload: Any = msgspec.json.decode(payload_data)
                        except (msgspec.DecodeError, TypeError):
                            pass
                        else:
                            logged_paths: set[tuple[str, ...]] = set()

                            for path, payload_path, _ in flattened_errors:
                                if not path or payload_path in logged_paths:
                                    continue

                                logged_paths.add(payload_path)
                                payload_piece: Any = payload

                                try:
                                    for key in payload_path:
                                        payload_piece = (
                                            payload_piece[int(key)]
                                            if isinstance(payload_piece, list)
                                            else payload_piece[key]
                                        )
                                except (IndexError, KeyError, TypeError, ValueError):
                                    logging.debug(
                                        "Discord request payload at %s: <missing>", path
                                    )
                                else:
                                    logging.debug(
                                        "Discord request payload at %s: %r",
                                        path,
                                        payload_piece,
                                    )

                    if details:
                        detail_text: str = "\n".join(details)
                        error.args = (f"{error}\n{detail_text}",)

            raise

    def _send_request(
        self: Self, method: str, url: str, request: dict[str, Any]
    ) -> Response:
        """Send a synchronous Webhook request with rate-limit retries."""
        with Session() as session:
            response: Response = session.request(method, url, **request)

            logging.debug(f"{response.request=}")
            logging.debug(f"{response.status_code=} {response.text=}")

            while response.status_code == 429:
                sleep(self._ratelimit_retry(response))

                response = session.request(method, url, **request)

            return self._raise_for_status(response, request)

    async def _send_request_async(
        self: Self, method: str, url: str, request: dict[str, Any]
    ) -> Response:
        """Send an asynchronous Webhook request with rate-limit retries."""
        async with AsyncSession() as session:
            response: Response = await session.request(method, url, **request)

            logging.debug(f"{response.request=}")
            logging.debug(f"{response.status_code=} {response.text=}")

            while response.status_code == 429:
                await async_sleep(self._ratelimit_retry(response))

                response = await session.request(method, url, **request)

            return self._raise_for_status(response, request)

    def _ratelimit_retry(self: Self, res: Response) -> float:
        """Return the amount of time to wait after encountering a ratelimit."""
        delay: float = 5.0
        res_data: Any = res.json()

        if isinstance(res_data, dict) and res_data.get("retry_after"):
            delay = res_data["retry_after"]

        logging.warning(f"Rate-limited, sleeping for {delay:,}s...")

        return delay
