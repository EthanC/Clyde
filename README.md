![Clyde](/assets/readme_banner.png)

![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ethanc/clyde/workflow.yaml)
![PyPI Downloads](https://img.shields.io/pypi/dm/discord-clyde)
[![Coverage Report](https://codecov.io/gh/ethanc/clyde/branch/main/graph/badge.svg)](https://codecov.io/gh/ethanc/clyde)

Clyde is a modern, type-hinted Python library for seamless interaction with the [Discord](https://discord.com/) Webhook API.

It's lightweight, developer-friendly, and supports advanced features like [Components](https://discord.com/developers/docs/components/overview) and [Embeds](https://discord.com/developers/docs/resources/message#embed-object).

## Features

-   Fully type-hinted for an excellent developer experience
-   Input validation powered by [msgspec](https://github.com/jcrist/msgspec)
-   Support for all Webhook-compatible [Components](https://discord.com/developers/docs/components/overview)
-   Granular customization of rich [Embeds](https://discord.com/developers/docs/resources/message#embed-object)
-   Helpers for Discord-flavored markdown, including timestamps
-   Compatible with both synchronous and asynchronous HTTP requests

## Getting Started

### Installation

> [!IMPORTANT]
> Clyde requires Python 3.10 or later.

Install with [uv](https://github.com/astral-sh/uv) (recommended):

```
uv add discord-clyde
```

Alternatively, install with pip:

```
pip install discord-clyde
```

### Examples

> [!TIP]
> Take the examples below and copy/paste them into your project to get started in seconds.

**Send a standard Message**

```py
from clyde import Webhook

relay: Webhook = Webhook(url="https://discord.com/api/webhooks/00000/XXXXXXXXXX")

relay.set_avatar_url("https://i.imgur.com/RzkhQgZ.png")
relay.set_username("Heisenberg")

relay.set_content("[Clyde](https://github.com/EthanC/Clyde) says hi!")

relay.execute()
```

![Preview](/assets/readme_example_standard.png)

**Send a Message with Components**

```py
from clyde import Webhook
from clyde.components import ActionRow, LinkButton, TextDisplay

relay: Webhook = Webhook(url="https://discord.com/api/webhooks/00000/XXXXXXXXXX")

relay.set_avatar_url("https://i.imgur.com/BpcKmVO.png")
relay.set_username("TARS")

greeting: TextDisplay = TextDisplay(content="[Clyde](https://github.com/EthanC/Clyde) says hi!")

actions: ActionRow = ActionRow()
repository: LinkButton = LinkButton()

repository.set_label("Try Clyde")
repository.set_url("https://github.com/EthanC/Clyde")

actions.add_component(repository)
relay.add_component(greeting)
relay.add_component(actions)
relay.execute()
```

![Preview](/assets/readme_example_components.png)

**Send a Message with an Embed**

```py
from clyde import Embed, Webhook


relay: Webhook = Webhook(url="https://discord.com/api/webhooks/00000/XXXXXXXXXX")

relay.set_avatar_url("https://i.imgur.com/QaTHttz.png")
relay.set_username("Shady")

rich: Embed = Embed()

rich.set_description("[Clyde](https://github.com/EthanC/Clyde) says hi!")
rich.set_color("#5865F2")

relay.add_embed(rich)
relay.execute()
```

![Preview](/assets/readme_example_embed.png)

## Releases

Clyde loosely follows [Semantic Versioning](https://semver.org/) for consistent, predictable releases.

## Contributing

Contributions are welcome—whether it’s fixing bugs or adding new features.

-   See [`CONTRIBUTING.md`](/.github/CONTRIBUTING.md) for guidelines.
-   See [Issues](https://github.com/EthanC/Clyde/issues) for known bugs and feature requests.

## Acknowledgements

The Clyde character and Discord brand assets are owned by Discord.

This project is not affiliated with or endorsed by Discord in any way.
