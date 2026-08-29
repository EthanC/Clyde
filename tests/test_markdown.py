from typing import cast

import pytest

from clyde import Markdown


def test_bulleted_list_indentation() -> None:
    """Format mixed bulleted-list items at every supported indentation level."""
    items: list[str | dict[str, str | int]] = ["Zero"]
    items.extend({"value": str(indent), "indent": indent} for indent in range(1, 11))

    expected: str = "\n".join(
        f"{'  ' * indent}- {value}"
        for indent, value in enumerate(
            ["Zero", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        )
    )

    assert Markdown.bulleted_list(items) == expected
    assert Markdown.bulleted_list([{"value": "Zero", "indent": 0}]) == "- Zero"
    assert Markdown.bulleted_list([]) == ""


def test_bulleted_list_dictionary_keys() -> None:
    """Reject dictionary items that do not have exactly the supported keys."""
    error: str = 'must contain only "value" and "indent"'

    with pytest.raises(ValueError, match=error):
        Markdown.bulleted_list([{"value": "Missing indent"}])

    with pytest.raises(ValueError, match=error):
        Markdown.bulleted_list(
            [{"value": "Extra key", "indent": 0, "other": "unsupported"}]
        )


def test_bulleted_list_dictionary_values() -> None:
    """Reject invalid bulleted-list dictionary values."""
    with pytest.raises(TypeError, match='"value" must be a string'):
        Markdown.bulleted_list([{"value": 1, "indent": 0}])

    with pytest.raises(TypeError, match='"indent" must be an integer'):
        Markdown.bulleted_list([{"value": "Item", "indent": "1"}])

    with pytest.raises(TypeError, match='"indent" must be an integer'):
        Markdown.bulleted_list([{"value": "Item", "indent": True}])

    with pytest.raises(ValueError, match='"indent" must be between 0 and 10'):
        Markdown.bulleted_list([{"value": "Item", "indent": -1}])

    with pytest.raises(ValueError, match='"indent" must be between 0 and 10'):
        Markdown.bulleted_list([{"value": "Item", "indent": 11}])

    with pytest.raises(TypeError, match="must be strings or dictionaries"):
        Markdown.bulleted_list([cast(str, 1)])
