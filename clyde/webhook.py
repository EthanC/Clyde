"""Define the Webhook class and its associates."""

import logging
from enum import IntEnum, StrEnum
from typing import Literal, Self, TypeAlias

import httpx
from httpx import AsyncClient, Response
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from clyde.components.action_row import ActionRow
from clyde.components.container import Container
from clyde.components.file import File
from clyde.components.media_gallery import MediaGallery
from clyde.components.section import Section
from clyde.components.seperator import Seperator
from clyde.components.text_display import TextDisplay
from clyde.embed import Embed
from clyde.poll import Poll

TopLevelComponent: TypeAlias = (
    ActionRow | Container | File | MediaGallery | Section | Seperator | TextDisplay
)


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


class AllowedMentions(BaseModel):
    """
    Represent the Allowed Mentions object on a Discord message.

    The Allowed Mention field allows for more granular control over mentions. This will
    always validate against the message and Components to avoid phantom pings. If
    allowed_mentions is not passed in, the mentions will be parsed via the content.

    https://discord.com/developers/docs/resources/message#allowed-mentions-object
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Webhook class."""

    parse: list[AllowedMentionTypes] | None = Field(default=None)
    """An array of Allowed Mention Types to parse from the content."""

    roles: list[str] | None = Field(default=None, max_length=100)
    """Array of role_ids to mention (max size of 100)."""

    users: list[str] | None = Field(default=None, max_length=100)
    """Array of user_ids to mention (max size of 100)."""

    replied_user: bool | None = Field(default=None)
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

        if not self.parse:
            self.parse = []

        if isinstance(parse, list):
            self.parse.extend(parse)
        else:
            self.parse.append(parse)

        return self

    def remove_parse(
        self: Self, parse: AllowedMentionTypes | list[AllowedMentionTypes] | int | None
    ) -> "AllowedMentions":
        """
        Remove an Allowed Mention Type from the Allowed Mentions instance.

        Arguments:
            parse (AllowedMentionTypes | list[AllowedMentionTypes] | int | None): An Allowed
                Mention Type, list of Allowed Mention Types, or an index to remove. If
                set to None, the parse value is cleared.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if self.parse:
            if parse:
                if isinstance(parse, list):
                    for entry in parse:
                        self.parse.remove(entry)
                elif isinstance(parse, int):
                    self.parse.pop(parse)
                else:
                    self.parse.remove(parse)

                # Do not retain an empty list
                if len(self.parse) == 0:
                    self.parse = None
            else:
                self.parse = None

        return self

    def add_role(self: Self, role: str | list[str]) -> "AllowedMentions":
        """
        Add a role ID to mention.

        Arguments:
            role (str | list[str]): A role ID or list of role IDs to add.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if self.parse and AllowedMentionTypes.ROLE_MENTIONS in self.parse:
            # No need for role if we already have ROLE_MENTIONS
            return self

        if not self.roles:
            self.roles = []

        if isinstance(role, list):
            self.roles.extend(role)
        else:
            self.roles.append(role)

        return self

    def remove_role(
        self: Self, role: str | list[str] | int | None
    ) -> "AllowedMentions":
        """
        Remove a role ID from the Allowed Mentions instance.

        Arguments:
            role (str | list[str] | int | None): A role ID, list of role IDs, or an index
                to remove. If set to None, the roles value is cleared.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if self.roles:
            if role:
                if isinstance(role, list):
                    for entry in role:
                        self.roles.remove(entry)
                elif isinstance(role, int):
                    self.roles.pop(role)
                else:
                    self.roles.remove(role)

                # Do not retain an empty list
                if len(self.roles) == 0:
                    self.roles = None
            else:
                self.roles = None

        return self

    def add_user(self: Self, user: str | list[str]) -> "AllowedMentions":
        """
        Add a user ID to mention.

        Arguments:
            user (str | list[str]): A user ID or list of user IDs to add.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if self.parse and AllowedMentionTypes.USER_MENTIONS in self.parse:
            # No need for user if we already have USER_MENTIONS
            return self

        if not self.users:
            self.users = []

        if isinstance(user, list):
            self.users.extend(user)
        else:
            self.users.append(user)

        return self

    def remove_user(
        self: Self, user: str | list[str] | int | None
    ) -> "AllowedMentions":
        """
        Remove a user ID from the Allowed Mentions instance.

        Arguments:
            user (str | list[str] | int | None): A user ID, list of user IDs, or an index
                to remove. If set to None, the users value is cleared.

        Returns:
            self (AllowedMentions): The modified Allowed Mentions instance.
        """
        if self.users:
            if user:
                if isinstance(user, list):
                    for entry in user:
                        self.users.remove(entry)
                elif isinstance(user, int):
                    self.users.pop(user)
                else:
                    self.users.remove(user)

                # Do not retain an empty list
                if len(self.users) == 0:
                    self.users = None
            else:
                self.users = None

        return self

    def set_replied_user(self: Self, replied_user: bool | None) -> "AllowedMentions":
        """
        Set whether to mention the author of the message being replied to.

        Arguments:
            replied_user (bool | None): True to mention the author. If set to None, the
                replied_user value is cleared.

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


class Webhook(BaseModel):
    """
    Represent a Discord Webhook object.

    Webhooks are a low-effort way to post messages to channels in Discord. They do not
    require a bot user or authentication to use.

    https://discord.com/developers/docs/resources/webhook

    Attributes:
        url (str | HttpUrl | None): The URL used for executing the Webhook.

        content (str | None): The message contents (up to 2000 characters).

        username (str | None): Override the default username of the Webhook.

        avatar_url (str | None): Override the default avatar of the Webhook.

        tts (bool | None): True if this is a TTS message.

        embeds (list[Embed] | None): Embedded rich content.

        allowed_mentions (AllowedMentions | None): Allowed mentions for the message.

        components (list[TopLevelComponent] | None): The Components to include with the message.

        files (list[None] | None): The contents of the file being sent.

        attachments (list[None] | None): Attachment objects with filename and description.

        flags (int | None): Message Flags combined as a bitfield.

        thread_name (str | None): Name of thread to create (requires the Webhook channel
            to be a forum or media channel).

        applied_tags (list[str] | None): Array of tag ids to apply to the thread (requires
            the Webhook channel to be a forum or media channel).

        poll (Poll | None): A Poll!

        _query_params (dict[str, str]): Additional query parameters to append to the URL.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)
    """Pydantic configuration for the Webhook class."""

    url: str | HttpUrl | None = Field(default=None, exclude=True)
    """The URL used for executing the Webhook."""

    content: str | None = Field(default=None, max_length=2000)
    """The message contents (up to 2000 characters)."""

    username: str | None = Field(default=None)
    """Override the default username of the Webhook."""

    avatar_url: str | None = Field(default=None)
    """Override the default avatar of the Webhook."""

    tts: bool | None = Field(default=None)
    """True if this is a TTS message."""

    embeds: list[Embed] | None = Field(default=None, max_length=10)
    """Embedded rich content."""

    allowed_mentions: AllowedMentions | None = Field(default=None)
    """Allowed mentions for the message."""

    components: list[TopLevelComponent] | None = Field(default=None)
    """The Components to include with the message."""

    files: None = Field(default=None)
    """The contents of the file being sent."""

    attachments: None = Field(default=None)
    """Attachment objects with filename and description."""

    flags: int | None = Field(default=None)
    """Message Flags combined as a bitfield."""

    thread_name: str | None = Field(default=None)
    """Name of thread to create (requires the Webhook channel to be a forum or media channel)."""

    applied_tags: list[str] | None = Field(default=None)
    """Array of tag ids to apply to the thread (requires the Webhook channel to be a forum or media channel)."""

    poll: Poll | None = Field(default=None)
    """A Poll!"""

    _query_params: dict[str, str] = {}
    """Additional query parameters to append to the URL."""

    def execute(self: Self) -> Response:
        """
        Execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.
        """
        if not self.url:
            raise ValueError("Webhook URL cannot be None")

        res: Response = httpx.post(
            str(self.url),
            json=self.model_dump(exclude_none=True, serialize_as_any=True),
            params=self._query_params,
        )

        logging.debug(f"{res.request.method=} {res.request.content=}")
        logging.debug(f"{res.status_code=} {res.text=}")

        return res.raise_for_status()

    async def execute_async(self: Self) -> Response:
        """
        Asynchronously execute the current Webhook instance.

        https://discord.com/developers/docs/resources/webhook#execute-webhook

        Returns:
            res (Response): Response object for the execution request.
        """
        if not self.url:
            raise ValueError("Webhook URL cannot be None")

        async with AsyncClient() as client:
            res: Response = await client.post(
                str(self.url),
                json=self.model_dump(exclude_none=True, serialize_as_any=True),
                params=self._query_params,
            )

        logging.debug(f"{res.request.method=} {res.request.content=}")
        logging.debug(f"{res.status_code=} {res.text=}")

        return res.raise_for_status()

    def set_url(self: Self, url: str) -> "Webhook":
        """
        Set the URL of the Webhook.

        Arguments:
            url (str): A Discord Webhook URL.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.url = HttpUrl(url)

        return self

    def set_content(self: Self, content: str | None) -> "Webhook":
        """
        Set the message content of the Webhook.

        Arguments:
            content (str | None): Message content. If set to None, the message content
                is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.content = content

        return self

    def set_username(self: Self, username: str | None) -> "Webhook":
        """
        Set the username of the Webhook instance.

        Arguments:
            username (str | None): A username. If set to None, the username is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        self.username = username

        return self

    def set_avatar_url(self: Self, avatar_url: str | None) -> "Webhook":
        """
        Set the avatar URL of the Webhook instance.

        Arguments:
            avatar_url (str | None): An image URL. If set to None, the avatar_url is cleared.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if avatar_url:
            avatar_url = str(HttpUrl(avatar_url))

        self.avatar_url = avatar_url

        return self

    def set_tts(self: Self, tts: bool | None) -> "Webhook":
        """
        Set whether the Webhook instance is a text-to-speech message.

        Arguments:
            tts (bool | None): Toggle text-to-speech functionality. If set to None, the
                tts value is cleared.

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
        if not self.embeds:
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
            embed (Embed | list[Embed] | int | None): An Embed, list of Embeds, or an index
                to remove. If set to None, all Embeds are removed.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if self.embeds:
            if embed:
                if isinstance(embed, list):
                    for entry in embed:
                        self.embeds.remove(entry)
                elif isinstance(embed, int):
                    self.embeds.pop(embed)
                else:
                    self.embeds.remove(embed)

                # Do not retain an empty list
                if len(self.embeds) == 0:
                    self.embeds = None
            else:
                self.embeds = None

        return self

    def set_allowed_mentions(
        self: Self, allowed_mentions: AllowedMentions | None
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
        self: Self, component: TopLevelComponent | list[TopLevelComponent]
    ) -> "Webhook":
        """
        Add a Component to the Webhook instance.

        Arguments:
            component (TopLevelComponent | list[TopLevelComponent]): A Component or list
                of Components.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if not self.components:
            self.components = []

        if not self.get_flag(MessageFlags.IS_COMPONENTS_V2):
            self.set_flag(MessageFlags.IS_COMPONENTS_V2, True)

        self._set_with_components(True)

        if isinstance(component, list):
            self.components.extend(component)
        else:
            self.components.append(component)

        return self

    def remove_component(
        self: Self, component: TopLevelComponent | list[TopLevelComponent] | int | None
    ) -> "Webhook":
        """
        Remove a Component from the Webhook instance.

        Arguments:
            component (TopLevelComponent | list[TopLevelComponent] | int | None): A Component,
                list of Components, or an index to remove. If set to None, all Components
                are removed.

        Returns:
            self (Webhook): The modified Webhook instance.
        """
        if self.components:
            if component:
                if isinstance(component, list):
                    for entry in component:
                        self.components.remove(entry)
                elif isinstance(component, int):
                    self.components.pop(component)
                else:
                    self.components.remove(component)

                # Do not retain an empty list
                if len(self.components) == 0:
                    self.components = None
            else:
                self.components = None

        # Do not retain unused values
        if not self.components:
            self._set_with_components(None)
            self.set_flag(MessageFlags.IS_COMPONENTS_V2, None)

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
        if not self.flags:
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
        if self.flags and (self.flags & flag):
            return True

        return False

    def set_thread_name(self: Self, thread_name: str | None) -> "Webhook":
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

    @field_validator("url", mode="after")
    @classmethod
    def _validate_url(cls, url: str | HttpUrl) -> HttpUrl:
        """
        Validate whether the value of URL is a valid Discord Webhook URL.

        Arguments:
            url (str | HttpUrl): A URL to validate.

        Returns:
            url (HttpUrl): The validate Webhook URL value.
        """
        if isinstance(url, str):
            url = HttpUrl(url)

        if url.scheme.lower() != "https":
            raise ValueError("Webhook URL scheme is not HTTPS")
        elif not url.host or url.host.lower() not in [
            "discord.com",
            "canary.discord.com",
        ]:
            raise ValueError("Webhook URL host is not a Discord domain")
        elif not url.path or not url.path.lower().startswith("/api/webhooks/"):
            raise ValueError("Webhook URL path is not valid")

        return url
