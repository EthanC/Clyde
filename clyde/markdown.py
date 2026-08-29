"""Define the Markdown class and its associates."""

from collections.abc import Sequence


class Markdown:
    """
    Define static methods for applying Discord-flavored Markdown formatting.

    Want to inject some flavor into your everyday text chat? You're in luck! Discord uses
    Markdown, a simple plain text formatting system that'll help you make your sentences
    stand out.

    https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline
    """

    @staticmethod
    def bold(content: str) -> str:
        """
        Format the provided content as bold.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as bold.
        """
        return f"**{content}**"

    @staticmethod
    def italics(content: str) -> str:
        """
        Format the provided content as italics.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as italics.
        """
        return f"*{content}*"

    @staticmethod
    def strikethrough(content: str) -> str:
        """
        Format the provided content as strikethrough.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as strikethrough.
        """
        return f"~~{content}~~"

    @staticmethod
    def block_quote(content: str, multi_line: bool = True) -> str:
        """
        Format the provided content as a block quote.

        Arguments:
            content (str): The content to format.

            multi_line (bool): Whether to use a multi-line block quote. Default is True.

        Returns:
            content (str): Content formatted as a block quote.
        """
        if multi_line:
            return f">>> {content}"
        else:
            return f"> {content}"

    @staticmethod
    def inline_code(content: str) -> str:
        """
        Format the provided content as inline code.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as inline code.
        """
        return f"`{content}`"

    @staticmethod
    def code_block(content: str, highlight: str | None = None) -> str:
        """
        Format the provided content as a code block.

        Arguments:
            content (str): The content to format.
            highlight (str | None): The language for syntax highlighting.

        Returns:
            content (str): Content formatted as a code block.
        """
        if not highlight:
            highlight = ""

        return f"```{highlight}\n{content}\n```"

    @staticmethod
    def spoiler(content: str) -> str:
        """
        Format the provided content as a spoiler.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as a spoiler.
        """
        return f"||{content}||"

    @staticmethod
    def underline(content: str) -> str:
        """
        Format the provided content as underline.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as underline.
        """
        return f"__{content}__"

    @staticmethod
    def header_1(content: str) -> str:
        """
        Format the provided content as header 1.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as a header 1.
        """
        return f"# {content}"

    @staticmethod
    def header_2(content: str) -> str:
        """
        Format the provided content as header 2.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as a header 2.
        """
        return f"## {content}"

    @staticmethod
    def header_3(content: str) -> str:
        """
        Format the provided content as header 3.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as a header 3.
        """
        return f"### {content}"

    @staticmethod
    def subtext(content: str) -> str:
        """
        Format the provided content as subtext.

        Arguments:
            content (str): The content to format.

        Returns:
            content (str): Content formatted as subtext.
        """
        result: str = ""

        for line in content.splitlines():
            line = line.strip()

            if line == "":
                result += "\n"

                continue

            result += f"-# {line}\n"

        return result.strip()

    @staticmethod
    def masked_link(content: str, url: str) -> str:
        """
        Format the provided content as a masked link.

        Arguments:
            content (str): The content to format.

            url (str): The URL to link to.

        Returns:
            content (str): Content formatted as a masked link.
        """
        return f"[{content}]({url})"

    @staticmethod
    def bulleted_list(items: Sequence[str | dict[str, str | int]]) -> str:
        """
        Format the provided items as a bulleted list.

        Arguments:
            items (list[str | dict[str, str | int]]): A list of items to format. A
                dictionary item must contain a string ``value`` and an integer
                ``indent`` from 0 through 10.

        Returns:
            content (str): Items formatted as a bulleted list.
        """
        result: list[str] = []

        for entry in items:
            if isinstance(entry, str):
                value: str = entry
                indent: int = 0
            elif isinstance(entry, dict):
                if set(entry) != {"value", "indent"}:
                    raise ValueError(
                        'Bulleted list dictionaries must contain only "value" and '
                        '"indent"'
                    )

                value = entry["value"]
                indent = entry["indent"]

                if not isinstance(value, str):
                    raise TypeError('Bulleted list dictionary "value" must be a string')

                if type(indent) is not int:
                    raise TypeError(
                        'Bulleted list dictionary "indent" must be an integer'
                    )

                if not 0 <= indent <= 10:
                    raise ValueError(
                        'Bulleted list dictionary "indent" must be between 0 and 10'
                    )
            else:
                raise TypeError("Bulleted list items must be strings or dictionaries")

            result.append(f"{'  ' * indent}- {value}")

        return "\n".join(result)

    @staticmethod
    def numbered_list(items: Sequence[str | dict[str, str | int]]) -> str:
        """
        Format the provided items as a numbered list.

        Arguments:
            items (list[str | dict[str, str | int]]): A list of items to format. A
                dictionary item must contain a string ``value`` and an integer
                ``indent`` from 0 through 11.

        Returns:
            content (str): Items formatted as a numbered list.
        """
        result: list[str] = []

        for number, entry in enumerate(items, start=1):
            if isinstance(entry, str):
                value: str = entry
                indent: int = 0
            elif isinstance(entry, dict):
                if set(entry) != {"value", "indent"}:
                    raise ValueError(
                        'Numbered list dictionaries must contain only "value" and '
                        '"indent"'
                    )

                value = entry["value"]
                indent = entry["indent"]

                if not isinstance(value, str):
                    raise TypeError('Numbered list dictionary "value" must be a string')

                if type(indent) is not int:
                    raise TypeError(
                        'Numbered list dictionary "indent" must be an integer'
                    )

                if not 0 <= indent <= 11:
                    raise ValueError(
                        'Numbered list dictionary "indent" must be between 0 and 11'
                    )
            else:
                raise TypeError("Numbered list items must be strings or dictionaries")

            result.append(f"{'   ' * indent}{number}. {value}")

        return "\n".join(result)
