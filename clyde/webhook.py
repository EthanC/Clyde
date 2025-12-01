"""Define the Webhook class and its associates."""

import logging
from asyncio import sleep as async_sleep
from enum import IntEnum, StrEnum
from pathlib import Path
from time import sleep
from typing import Annotated, Any, Iterable, Literal, Self, Tuple, TypeAlias

import httpx
import msgspec
from httpx import Request, Response
from msgspec import UNSET, Meta, Struct, UnsetType

from clyde.attachment import Attachment
from clyde.components.action_row import ActionRow
from clyde.components.container import Container
from clyde.components.file import File
from clyde.components.media_gallery import MediaGallery
from clyde.components.section import Section
from clyde.components.seperator import Seperator
from clyde.components.text_display import TextDisplay
from clyde.embed import Embed
from clyde.poll import Poll
from clyde.validation import Validation

TopLevelComponent: TypeAlias = (
    ActionRow | Container | File | MediaGallery | Section | Seperator | TextDisplay
)
TopLevelComponents: TypeAlias = list[TopLevelComponent]


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


class Webhook(Struct, kw_only=True):
    """
    Represent a Discord Webhook object.

    Webhooks are a low-effort way to post messages to channels in Discord. They do not
    require a bot user or authentication to use.

    https://discord.com/developers/docs/resources/webhook

    Attributes:
        url (str): The URL used for executing the Webhook.

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
    """The URL used for executing the Webhook."""

    content: UnsetType | Annotated[str, Meta(max_length=2000)] = msgspec.field(
        default=UNSET
    )
    """The message contents (up to 2000 characters)."""

    username: UnsetType | str = msgspec.field(default=UNSET)
    """Override the default username of the Webhook."""

    avatar_url: UnsetType | str = msgspec.field(default=UNSET)
    """Override the default avatar of the Webhook."""

    tts: UnsetType | bool = msgspec.field(default=UNSET)
    """True if this is a TTS message."""

    embeds: UnsetType | Annotated[list[Embed], Meta(min_length=1, max_length=10)] = (
        msgspec.field(default=UNSET)
    )
    """Embedded rich content."""

    allowed_mentions: UnsetType | AllowedMentions = msgspec.field(default=UNSET)
    """Allowed mentions for the message."""

    components: UnsetType | list[TopLevelComponent] = msgspec.field(default=UNSET)
    """The Components to include with the message."""

    flags: UnsetType | int = msgspec.field(default=UNSET)
    """Message Flags combined as a bitfield."""

    thread_name: UnsetType | str = msgspec.field(default=UNSET)
    """Name of thread to create (requires the Webhook channel to be a forum or media channel)."""

    applied_tags: UnsetType | list[str] = msgspec.field(default=UNSET)
    """Array of tag ids to apply to the thread (requires the Webhook channel to be a forum or media channel)."""

    poll: UnsetType | Poll = msgspec.field(default=UNSET)
    """A Poll!"""

    _attachments: list[Attachment] = []
    """Attachment objects to include with the payload."""

    _query_params: dict[str, str] = {}
    """Additional query parameters to append to the URL."""

    def execute(self: Self) -> Response:
        """
        Execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.
        """
        self._validate()

        with httpx.Client(params=self._query_params) as client:
            req: Request = self._build_request(client)
            res: Response = client.send(req)

            res.request.read()

            logging.debug(f"{res.request.method=} {res.request.content=}")
            logging.debug(f"{res.status_code=} {res.text=}")

            while res.status_code == 429:
                delay: float = self._ratelimit_retry(res)

                sleep(delay)

                res = client.send(req)

            return res.raise_for_status()

    async def execute_async(self: Self) -> Response:
        """
        Asynchronously execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.
        """
        self._validate()

        async with httpx.AsyncClient(params=self._query_params) as client:
            req: Request = self._build_request(client)
            res: Response = await client.send(req)

            res.request.read()

            logging.debug(f"{res.request.method=} {res.request.content=}")
            logging.debug(f"{res.status_code=} {res.text=}")

            while res.status_code == 429:
                delay: float = self._ratelimit_retry(res)

                async_sleep(delay)

                res = await client.send(req)

            return res.raise_for_status()

    def set_content(
        self: Self, content: UnsetType | str, fallback: bool = False
    ) -> "Webhook":
        """
        Set the message content of the Webhook.

        Arguments:
            content (str): Message content. If set to None, the message content
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
        if isinstance(self.embeds, UnsetType):
            self.embeds = []

        if isinstance(embed, Embed):
            self.embeds.append(embed)
        else:
            self.embeds.extend(embed)

        return self

    def remove_embed(self: Self, embed: Embed | list[Embed] | int) -> "Webhook":
        """
        Remove embedded rich content from the Webhook instance.

        Arguments:
            embed (Embed | list[Embed] | int | None): An Embed, list of Embeds, or an index
                to remove. If set to None, all Embeds are removed.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if isinstance(self.embeds, list):
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
        self: Self, allowed_mentions: UnsetType | AllowedMentions
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
        """
        if isinstance(self.components, UnsetType):
            self.components = []

        if not self.get_flag(MessageFlags.IS_COMPONENTS_V2):
            self.set_flag(MessageFlags.IS_COMPONENTS_V2, True)

        self._set_with_components(True)

        if isinstance(component, TopLevelComponent):
            self.components.append(component)
        elif isinstance(component, Iterable):
            self.components.extend(component)

        return self

    def remove_component(
        self: Self, component: TopLevelComponent | list[TopLevelComponent] | int
    ) -> "Webhook":
        """
        Remove a Component from the Webhook instance.

        Arguments:
            component (TopLevelComponent | list[TopLevelComponent] | int): A Component,
                list of Components, or an index to remove.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if isinstance(self.components, list):
            if isinstance(component, TopLevelComponent):
                self.components.remove(component)
            elif isinstance(component, int):
                self.components.pop(component)
            else:
                self.components = [
                    entry for entry in self.components if entry not in component
                ]

            # Do not retain an empty list
            if len(self.components) == 0:
                self.components = UNSET

        return self

    def add_attachment(
        self: Self, filename: str, content: bytes | Path, spoiler: bool = False
    ) -> "Webhook":
        """
        Add a file Attachment to the Webhook instance.

        Arguments:
            filename (str): Name of the file to attach.

            content (bytes | Path): Binary content of the file to attach.
                If a Path is passed, the referenced file will be read.

            spoiler (bool): True if the file should be a spoiler (blurred).

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if isinstance(content, Path):
            with open(content, "rb") as handle:
                content = handle.read()

        attachment: Attachment = Attachment(filename=filename, content=content)

        if spoiler:
            attachment.set_spoiler(True)

        self._attachments.append(attachment)

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
        if isinstance(self.flags, UnsetType):
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
            poll (Poll): A Discord Poll object.

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
            if self._query_params.get(key):
                self._query_params.pop(key)
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
            if self._query_params.get(key):
                self._query_params.pop(key)
        else:
            self._query_params[key] = thread_id

        return self

    def _set_with_components(self: Self, with_components: bool | None) -> "Webhook":
        """
        Set whether the Webhook instance uses the with_components query parameter.

        Arguments:
            with_components (bool | None): Toggle with_components query parameter. If set
                to None, the with_components parameter is removed.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        key: str = "with_components"

        if with_components is None:
            if self._query_params.get(key):
                self._query_params.pop(key)
        else:
            self._query_params[key] = str(with_components)

        return self

    def _validate(self: Self) -> None:
        """Convert applicable data types prior to Webhook serialization."""
        if isinstance(self.embeds, list):
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

    def _build_request(self: Self, client: httpx.Client | httpx.AsyncClient) -> Request:
        """Return a Request object for the Webhook instance."""
        if len(self._attachments) > 0:
            files: dict[str, Tuple[str | Literal[None], str | bytes]] = {
                "payload_json": (None, msgspec.json.encode(self))
            }

            for attachment in self._attachments:
                if isinstance(attachment.filename, UnsetType):
                    continue
                elif isinstance(attachment.content, UnsetType):
                    continue

                files[attachment.filename] = (attachment.filename, attachment.content)

            return client.build_request("POST", self.url, files=files)

        return client.build_request(
            "POST",
            self.url,
            content=msgspec.json.encode(self),
            headers={"Content-Type": "application/json"},
        )

    def _ratelimit_retry(self: Self, res: Response) -> float:
        """Return the amount of time to wait after encountering a ratelimit."""
        delay: float = 5.0
        res_data: Any = res.json()

        if isinstance(res_data, dict) and res_data.get("retry_after"):
            delay = res_data["retry_after"]

        logging.warning(f"Rate-limited, sleeping for {delay:,}s...")

        return delay
