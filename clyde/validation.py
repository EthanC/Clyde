"""Define the Validation class and its associates."""

from datetime import datetime

from pydantic import AnyUrl


class Validation:
    """Define static methods for reusable data validation and conversion."""

    @staticmethod
    def validate_color(value: str | int) -> int:
        """
        Validate—and convert, if applicable—a color value for Discord.

        Arguments:
            value (str | int): The value to validate.

        Returns:
            value (int): The validated color value.
        """
        if isinstance(value, str):
            if value.startswith("#"):
                # Discard the # in a hex color code
                value = value[1:]

            value = int(value, base=16)

        return value

    @staticmethod
    def validate_timestamp(value: int | float | str | datetime) -> str:
        """
        Validate—and convert, if applicable—a timestamp value for Discord.

        Arguments:
            value (int | float | str | datetime): The value to validate.

        Returns:
            value (str): The validated value.
        """
        if isinstance(value, int):
            value = datetime.fromtimestamp(float(value))
        elif isinstance(value, float):
            value = datetime.fromtimestamp(value)
        elif isinstance(value, str):
            value = datetime.fromisoformat(value)

        return value.isoformat()

    @staticmethod
    def validate_url_scheme(value: str | None, valid_scheme: list[str]) -> str:
        """
        Validate a URL value contains a valid scheme.

        Arguments:
            value (str): The URL to validate.

            valid_scheme (list[str]): A list of valid URL schemes.

        Returns:
            value (str): The validated URL.
        """
        if not value:
            raise ValueError(
                f"Empty URL is not valid for scheme(s) {', '.join(valid_scheme)}"
            )

        scheme: str = AnyUrl(value).scheme.lower()
        valid_scheme = [_scheme.lower() for _scheme in valid_scheme]

        if scheme not in valid_scheme:
            raise ValueError(
                f"URL {value} is not valid for scheme(s) {', '.join(valid_scheme)}"
            )

        return value
