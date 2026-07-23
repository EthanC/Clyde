![Clyde](images/readme_banner.png)

<p align="center"><strong>Build rich Discord Webhook API interactions with a typed Python API.</strong></p>

Clyde supports plain messages, [Components](https://discord.com/developers/docs/components/overview), and rich [Embeds](https://discord.com/developers/docs/resources/message#embed-object) for the [Discord Webhook API](https://discord.com/developers/docs/resources/webhook). It validates each payload and sends it through synchronous or asynchronous HTTP methods.

## Features

- Type annotations across the public API
- Input type and field validation with [msgspec](https://github.com/jcrist/msgspec)
- Plain content, every webhook-compatible Discord Component, and field-level Embed controls
- Helpers for Discord-flavored Markdown and timestamps
- Synchronous and asynchronous HTTP requests through [niquests](https://github.com/jawah/niquests)
- Automatic retries when Discord returns a rate limit
- API reference pages generated with [Zensical](https://github.com/zensical/zensical)

## Installation

**Clyde requires Python 3.11 or later.**

Add Clyde to a [uv](https://github.com/astral-sh/uv) project:

```console
uv add discord-clyde
```

The package is also available through pip:

```console
pip install discord-clyde
```

## Examples

### Plain Message

```py
from clyde import Webhook

Webhook(
    url="https://discord.com/api/webhooks/00000/XXXXXXXXXX",
    avatar_url="https://i.imgur.com/RzkhQgZ.png",
    username="Heisenberg",
    content="[Clyde](https://github.com/EthanC/Clyde) says hi!",
).execute()
```

### Message With Components

```py
from clyde import Webhook
from clyde.components import ActionRow, LinkButton, TextDisplay

webhook = Webhook(
    url="https://discord.com/api/webhooks/00000/XXXXXXXXXX",
    avatar_url="https://i.imgur.com/BpcKmVO.png",
    username="TARS",
)

webhook.add_component(
    [
        TextDisplay(content="[Clyde](https://github.com/EthanC/Clyde) says hi!"),
        ActionRow(
            components=[
                LinkButton(
                    label="Try Clyde",
                    url="https://github.com/EthanC/Clyde",
                )
            ]
        ),
    ]
).execute()
```

### Message With an Embed

```py
from clyde import Embed, Webhook

Webhook(
    url="https://discord.com/api/webhooks/00000/XXXXXXXXXX",
    avatar_url="https://i.imgur.com/QaTHttz.png",
    username="Shady",
    embeds=[
        Embed(
            description="[Clyde](https://github.com/EthanC/Clyde) says hi!",
            color="#5865F2",
        )
    ],
).execute()
```

## API Reference

- [Webhooks](webhook.md)
- [Messages](message.md)
- [Components](component.md)
- [Embeds](embed.md)
- [Attachments](attachment.md)
- [Polls](poll.md)
- [Markdown](markdown.md)
- [Timestamps](timestamp.md)
- [Validation](validation.md)

## Logging

Clyde emits records under the `clyde` logger. Webhook request records use `clyde.webhook`. The library does not set an application log level or configure an output handler.

```py
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("clyde").setLevel(logging.DEBUG)
```

| Level | Records |
| --- | --- |
| `DEBUG` | Request metadata, timings, status codes, and byte counts |
| `INFO` | Content fallbacks and recovery after rate limiting |
| `WARNING` | Rate-limit retries and skipped incomplete Attachments |

Logs exclude webhook credentials, request and response bodies, message content, and attachment data.
