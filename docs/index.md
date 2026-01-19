![Clyde](images/readme_banner.png)

Clyde is a modern, type-hinted Python library for seamless interaction with the [Discord](https://discord.com/) Webhook API.

It's lightweight, developer-friendly, and supports advanced features like [Components](https://discord.com/developers/docs/components/overview) and [Embeds](https://discord.com/developers/docs/resources/message#embed-object).

## Features

-   Fully type-hinted for an excellent developer experience
-   Input validation powered by [msgspec](https://github.com/jcrist/msgspec)
-   Support for all Webhook-compatible [Components](https://discord.com/developers/docs/components/overview)
-   Granular customization of rich Embeds
-   Helpers for Discord-flavored markdown, including timestamps
-   Compatible with both synchronous and asynchronous HTTP requests
-   Beautiful generated [documentation](https://clyde.e3n.im/) built with [Zensical](https://github.com/zensical/zensical)

## Getting Started

### Installation

**Clyde requires Python 3.11 or later.**

Install with [uv](https://github.com/astral-sh/uv) (recommended):

```
uv add discord-clyde
```

Alternatively, install with pip:

```
pip install discord-clyde
```
